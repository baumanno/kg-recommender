ids = dict()

with open('items_id.txt', 'r') as file:
    firstLine = True
    for line in file:
        if firstLine:
           firstLine = False
           continue

        contents = line.strip().split(' ')
        pre_pos = contents[1].split(':')
        ids[contents[0]] = f'http://www.netflix.com/nf-schema#{pre_pos[1]}'

output = list()
with open('recommendations.csv', 'r') as file:
    firstLine = True
    for line in file:
        if firstLine:
           firstLine = False
           continue

        contents = line.strip().split(' ')
        kgfileid = eval(f'{contents[0]} + 1')
        if kgfileid < 10:
           kgfileid = f'0{kgfileid}'

        output.append(f'userprofile_{kgfileid} {ids[contents[1]]} {contents[2]}')

with open('external_recos.txt', 'a') as file:
    for o in output:
       file.write(f'{o}\n')

