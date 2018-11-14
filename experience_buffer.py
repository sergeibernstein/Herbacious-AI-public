import numpy as np
import random


class ExperienceTree():
    PER_e = 0.01  # Hyperparameter that we use to avoid some experiences to have 0 probability of being taken
    PER_a = 0.6  # Hyperparameter that we use to make a tradeoff between taking only exp with high priority and sampling randomly
    PER_b = 0.4  # importance-sampling, from initial value increasing to 1
    PER_b_increment_per_sampling = 0.001
    absolute_error_upper = 10.  # clipped abs error

    def __init__(self, capacity_exp):
        self.data_pointer = 0
        self.capacity = 2 ** capacity_exp
        self.tree = np.zeros(2 * self.capacity - 1)
        self.data = list(np.zeros(self.capacity))

    def add(self, priority, data):
        if np.isnan(priority):
            print("Input to tree add is nan")
        # Look at what index we want to put the experience
        tree_index = self.data_pointer + self.capacity - 1

        """ tree:
            0
           / \
          0   0
         / \ / \
tree_index  0 0  0  We fill the leaves from left to right
        """

        # Update data frame
        self.data[self.data_pointer] = data

        # Update the leaf
        if np.isnan(priority):
            print("Nan input to update in add")
        self.update(tree_index, priority)

        # Add 1 to data_pointer
        self.data_pointer += 1

        if self.data_pointer >= self.capacity:  # If we're above the capacity, you go back to first index (we overwrite)
            self.data_pointer = 0

    """
    Update the leaf priority score and propagate the change through tree
    """

    def update(self, tree_index, priority):
        if np.isnan(priority):
            print("Got nan input to tree update")

        # Change = new priority score - former priority score
        change = priority - self.tree[tree_index]
        self.tree[tree_index] = priority

        if np.isnan(change):
            print("tree change is nan")


        # then propagate the change through tree
        while tree_index != 0:  # this method is faster than the recursive loop in the reference code

            """
            Here we want to access the line above
            THE NUMBERS IN THIS TREE ARE THE INDEXES NOT THE PRIORITY VALUES

                0
               / \
              1   2
             / \ / \
            3  4 5  [6] 

            If we are in leaf at index 6, we updated the priority score
            We need then to update index 2 node
            So tree_index = (tree_index - 1) // 2
            tree_index = (6-1)//2
            tree_index = 2 (because // round the result)
            """
            tree_index = (tree_index - 1) // 2
            if np.isnan(self.tree[tree_index]):
                print("old tree index is nan")
            self.tree[tree_index] += change
            if np.isnan(self.tree[tree_index]):
                print("new tree index is nan")

    """
    Here we get the leaf_index, priority value of that leaf and experience associated with that index
    """

    def get_leaf(self, v):
        """
        Tree structure and array storage:
        Tree index:
             0         -> storing priority sum
            / \
          1     2
         / \   / \
        3   4 5   6    -> storing priority for experiences
        Array type for storing:
        [0,1,2,3,4,5,6]
        """
        parent_index = 0

        while True:  # the while loop is faster than the method in the reference code
            left_child_index = 2 * parent_index + 1
            right_child_index = left_child_index + 1

            # If we reach bottom, end the search
            if left_child_index >= len(self.tree):
                leaf_index = parent_index
                break

            else:  # downward search, always search for a higher priority node

                if v <= self.tree[left_child_index]:
                    parent_index = left_child_index

                else:
                    v -= self.tree[left_child_index]
                    parent_index = right_child_index

        data_index = leaf_index - self.capacity + 1

        return leaf_index, self.tree[leaf_index], self.data[data_index]

    @property
    def total_priority(self):
        return self.tree[0]  # Returns the root node

    """
    Store a new experience in our tree
    Each new experience have a score of max_prority (it will be then improved when we use this exp to train our DDQN)
    """

    def store(self, experience):
        # Find the max priority
        max_priority = np.max(self.tree[-self.capacity:])

        # If the max priority = 0 we can't put priority = 0 since this exp will never have a chance to be selected
        # So we use a minimum priority
        if max_priority == 0:
            max_priority = self.absolute_error_upper

        if np.isnan(max_priority):
            print("Trying to add a nan max_priority")

        self.add(max_priority, experience)  # set the max p for new p

    def sample(self, batch_size=None):
        if batch_size is None:
            value = np.random.uniform(0, self.total_priority)

            index, priority, data = self.get_leaf(value)

            return index, data
        else:
            experience_pairs = []

            priority_interval = self.total_priority / batch_size

            for i in range(batch_size):
                value = np.random.uniform(i * priority_interval, (i + 1) * priority_interval)
                index, priority, data = self.get_leaf(value)
                experience_pairs += [(index, data)]

            #  IS = (1/N * 1/P(i))**b /max wi == (N*P(i))**-b  /max wi
            # b_ISWeights[i, 0] = np.power(n * sampling_probabilities, -self.PER_b)/ max_weight

            return experience_pairs



class ExperienceBuffer():

    def __init__(self, capacity_exp=16, num_multi_steps=3, gamma=1.0):
        self.experience_buffer = ExperienceTree(capacity_exp)
        self.capacity_exp = capacity_exp
        self.num_multi_steps = num_multi_steps
        self.gamma = gamma
        self.multi_step_memory = []

    def dump_memory_to_experience_buffer(self, reward=None):
        for memory in self.multi_step_memory:
            if reward is None:
                self.experience_buffer.store(memory[0])
            else:
                memory_reward = (self.gamma ** memory[1]) * reward
                new_experience = memory[0][:5] + (memory_reward,)
                self.experience_buffer.store(new_experience)
        self.multi_step_memory = []

    def add_experience(self, state_vec, action_index, possible_action_indexes, new_state_vec=None, new_possible_action_indexes=None, reward=None):
        experience_tuple = (state_vec, action_index, possible_action_indexes, new_state_vec, new_possible_action_indexes, reward)
        if action_index not in possible_action_indexes:  # We just tried to do something impossible
            self.experience_buffer.store(experience_tuple)
            self.dump_memory_to_experience_buffer()
        else:
            if reward != 0.0:  # GAME OVER
                self.experience_buffer.store(experience_tuple)
                self.dump_memory_to_experience_buffer(reward)
            else:
                self.multi_step_memory += [(experience_tuple, 0)]
                new_multi_step_memory = []
                for memory in self.multi_step_memory:
                    new_experience = (memory[0][0], memory[0][1], memory[0][2], new_state_vec.copy(), list(new_possible_action_indexes), memory[0][5])
                    new_memory = (new_experience, memory[1] + 1)
                    if new_memory[1] == self.num_multi_steps:
                        self.experience_buffer.store(new_experience)
                    else:
                        new_multi_step_memory += [new_memory]
                self.multi_step_memory = new_multi_step_memory

    def sample_experience(self, batch_size=None):
        return self.experience_buffer.sample(batch_size)

    def clear_buffer(self):
        self.experience_buffer = ExperienceTree(self.capacity_exp)
