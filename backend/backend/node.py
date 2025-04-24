class Node:
    def __init__(self, relay_name: str):
        self.left: Node | None | int = None
        self.right: Node | None | int = None

        self.relay_name = relay_name
        self.relay_index = int(relay_name[1])  # R1 -> 1
        self.polarity = False  # False/0 is right, True/1 is left

        self.in_use = False

    def to_next(self):
        # process to whichever switch is 'pointed to' by this switch
        if self.polarity:
            return self.left
        else:
            return self.right


MaybeNode = Node | int | None
