
import json
import sys
from global_methods import *

class SpatialMemory:
    def __init__(self, f_saved):
        self.spatial_tree = dict() #spactial dict
        if check_if_file_exists(f_saved):
            self.spatial_tree = json.load(open(f_saved))


    def save(self, out_json):
        with open(out_json, "w") as outfile:
            json.dump(self.spatial_tree, outfile)
        pass

    def print_tree(self):
        def _print_tree(tree, depth):
            dash = " >" * depth
            if type(tree) == type(list()):
                if tree:
                    print(dash, tree)
                return

            for key, val in tree.items():
                if key:
                    print(dash, key)
                _print_tree(val, depth + 1)

        _print_tree(self.spatial_tree, 0)

    def get_str_accessible_sectors(self, curr_world):
        '''
        현재 world에서 persona가 접근할 수 있는 모든 sector를 summary string 형태로 반환
        :param curr_world:
        :return:
        '''
        x = ", ".join(list(self.spatial_tree[curr_world].keys()))
        return x
        pass

    def get_str_accessible_sector_arenas(self, sector):
        """
        현재 sector에서 persona가 접근할 수 있는 모든 arena를 summary string 형태로 반환

        Note that there are places a given persona cannot enter. This information
        is provided in the persona sheet. We account for this in this function.

        INPUT
          None
        OUTPUT
          A summary string of all the arenas that the persona can access.
        EXAMPLE STR OUTPUT
          "bedroom, kitchen, dining room, office, bathroom"
        """
        curr_world, curr_sector = sector.split(":")
        if not curr_sector:
            return ""
        x = ", ".join(list(self.spatial_tree[curr_world][curr_sector].keys()))
        return x

    def get_str_accessible_arena_game_objects(self, arena):
        """
        Get a str list of all accessible game objects that are in the arena. If
        temp_address is specified, we return the objects that are available in
        that arena, and if not, we return the objects that are in the arena our
        persona is currently in.

        INPUT
          temp_address: optional arena address
        OUTPUT
          str list of all accessible game objects in the gmae arena.
        EXAMPLE STR OUTPUT
          "phone, charger, bed, nightstand"
        """
        curr_world, curr_sector, curr_arena = arena.split(":")

        if not curr_arena:
            return ""

        try:
            x = ", ".join(item["subject"] for item in self.spatial_tree[curr_world][curr_sector][curr_arena])
        except:
            x = ", ".join(item["subject"] for item in self.spatial_tree[curr_world][curr_sector][curr_arena.lower()])
        return x

if __name__ == '__main__':
    import os
    print("os path")
    print(os.getcwd())
    x = "../environment/persona/Isabella Rodriguez/spatial_memory.json"
    print(f"x : {x}")
    x = SpatialMemory(x)
    # x.print_tree()
    print(sys.path)
    print(x.get_str_accessible_sectors("the Ville"))
    # print("a")
    pass