class bandlogic:

    @staticmethod
    def find_highest_count(voodooObject):
        tmp = {}
        highest_hit = -1
        highest_name = "No Gigs"
        for child in voodooObject:
            if child.name not in tmp:
                tmp[child.name] = 0
            tmp[child.name] = len(child.gigs)

            if tmp[child.name] > highest_hit:
                highest_hit = tmp[child.name]
                highest_name = child.name
        return highest_hit, highest_name
