from dataloader import DataLoader
from tabulate import tabulate

myDataLoader = DataLoader()

# to ensure that data files are in place
myDataLoader.compile_files()

# Get all dialogues for any character from 'house', 'bigbangtheory', 'friends'
sheldon_dialogues_df = myDataLoader.get_all_dialogues('sheldon', 'bigbangtheory')
house_dialogues_df = myDataLoader.get_all_dialogues('house','house')

print(tabulate(sheldon_dialogues_df.head(), headers='keys', tablefmt='psql'))
print(tabulate(house_dialogues_df.head(), headers='keys', tablefmt='psql'))

# Get all pairs of dialogues for a character in a series
conversations_with_sheldon_df = myDataLoader.get_conversations_with('sheldon','bigbangtheory')
conversations_with_house_df = myDataLoader.get_conversations_with('house','house')

print(tabulate(conversations_with_sheldon_df.head(), headers='keys', tablefmt='psql'))
print(tabulate(conversations_with_house_df.head(), headers='keys', tablefmt='psql'))
