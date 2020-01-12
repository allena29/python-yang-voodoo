from yangvoodoo import Merge


merger = Merge.DataSchema('form', 'form-section',  'xml', ['test/resources/form.xml'], 'yang/')
# for x in merger._get_all_data_paths():
#     print(x)
# # print('-'*100)
# merger._build_map_of_predicates()
# print(merger.predicate_map)
# print(merger.predicate_path_count)
# print('-'*100)
# for x in merger._expand_list_instances():
#     print(x)

for x in merger.process():
    print(x)

print('---')
for y in merger.structures:
    print(y, merger.structures[y])
