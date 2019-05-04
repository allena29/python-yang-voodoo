class bandlogic:

    @staticmethod
    def find_highest_count(voodooObject):
        tmp = {}
        highest_hit = -1
        highest_name = "No Gigs"
        for child in voodooObject:
            if child.name not in tmp:
                tmp[child.name] = 0
            i = 0
            for childgig in child.gigs:
                i = i+1
            tmp[child.name] = i

            if tmp[child.name] > highest_hit:
                highest_hit = tmp[child.name]
                highest_name = child.name
        return highest_hit, highest_name

    @staticmethod
    def find_gig_piehcart(voodooObject):
        bands = voodooObject
        distribution = {}
        for band in bands:
            if len(band.gigs) not in distribution:
                distribution[len(band.gigs)] = 0
            distribution[len(band.gigs)] += 1

        return distribution
