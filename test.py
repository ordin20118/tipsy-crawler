

data = {
    'name_en': 123
}

isNE = 'name_en' in data
print(isNE)

isNK = 'name_kr' in data
print(isNK)


if (isNE is False) or (isNK is False):
    print("없다.")
else:
    print("있다.")