class ItemAccessor:
    @staticmethod
    def decompose_path(path):
        return path.split('.')

    @staticmethod
    def get_node(tree, nodes, target_node=None):
        if target_node is None:
            target_node = nodes[-1]

        if not isinstance(tree, dict) and len(nodes) > 1:
            return {
                "reason": "Tree is not a dict",
                "found": False,
                "value": None
            }

        # Get current item
        current_node = nodes.pop(0)

        if current_node != target_node:
            tree = tree.get(current_node)
            return ItemAccessor.get_node(tree, nodes)
        else:
            return tree.get(target_node)
