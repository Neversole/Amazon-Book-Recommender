##################################
# This code parses the amazon-meta.txt file and outputs products.csv and reviews.csv
##################################

import pandas as pd

# Create lists for reviews and entries to put dictionaries in
entry_list = []
reviews = []

# Create empty dictionaries for each entry ID
with open('amazon-meta.txt', encoding='utf8') as f:

    # List of ID's
    ids = []

    # Get every ID number from text file and add it the ID's list
    for line in f:
        if line.startswith('Id'):
            id = line.strip().split(':   ')[1]
            ids.append(id)

    # Create a dictionary for every ID in the ID's list
    # The dictionary values will all be empty except for the ID itself
    for id in ids:
        dict = {}
        dict['Id'] = id
        dict['ASIN'] = ''
        dict['title'] = ''
        dict['group'] = ''
        dict['salesrank'] = ''
        dict['similar'] = ''
        dict['categories'] = ''
        dict['reviewTotal'] = ''
        dict['downloaded'] = ''
        dict['avgRating'] = ''
        entry_list.append(dict)

f.close()

# Write values to dictionaries and add them to their respective list
with open('amazon-meta.txt', encoding='utf8') as f2:
    # Set for categories to be added to
    # This will prevent duplicates from being added
    categories_set = set()
    # Keep track of the current product ID
    indexId = 0
    # discontinued = 0

    for line in f2:
        # 5868 discontinued products
        # if line.startswith('  discon'):
        #     discontinued += 1
        # Get entry ID, update indexID and clear the categories_set
        if line.startswith('Id'):
            entryId = line.strip().split(':   ')[1]
            indexId = int(entryId)
            categories_set.clear()

        # Get ASIN
        if line.startswith('ASIN'):
            asin = line.strip().split(': ')[1]
            entry_list[indexId]['ASIN'] = asin

        # Get title
        if line.startswith('  title'):
            title = line.strip().split('title: ')[1]
            entry_list[indexId]['title'] = title

        # Get group
        if line.startswith('  group'):
            group = line.strip().split(': ')[1]
            entry_list[indexId]['group'] = group

        # Get salesrank
        if line.startswith('  salesrank'):
            srank = line.strip().split(': ')[1]
            entry_list[indexId]['salesrank'] = srank

        # Get entry reviews info
        if line.startswith('  reviews:'):
            reviewLine = line.strip().split()
            total = reviewLine[2]
            downloaded = reviewLine[4]
            avgRating = reviewLine[7]
            entry_list[indexId]['reviewTotal'] = total
            entry_list[indexId]['downloaded'] = downloaded
            entry_list[indexId]['avgRating'] = avgRating

        # Get similar products
        if line.startswith('  similar'):
            similarLine = line.strip().split()
            if similarLine[1] == '0':
                entry_list[indexId]['similar'] = ''
            else:
                # Remove first two items in list
                similarLine.pop(0)
                similarLine.pop(0)
                entry_list[indexId]['similar'] = ', '.join(str(elem) for elem in similarLine)

        # Get categories
        if line.startswith('   |'):
            category_key_words = line.strip().split('|')
            for item in category_key_words:
                cat = item.split('[')
                if cat[0] == '':
                    next
                else:
                    categories_set.add(cat[0])
            categories_string = ', '.join(categories_set)
            entry_list[indexId]['categories'] = categories_string

        # Get customer reviews info
        if line.startswith('    19') or line.startswith('    20'):
            custReview = line.strip().split()
            reviewDict = {}
            reviewDict['Id'] = str(indexId)
            reviewDict['Customer'] = custReview[2]
            reviewDict['Date'] = custReview[0]
            reviewDict['Rating'] = custReview[4]
            reviewDict['Votes'] = custReview[6]
            reviewDict['Helpful'] = custReview[8]
            reviews.append(reviewDict)
        else:
            next

f2.close()

# Convert lists of dictionaries to pandas dataframes and write them to CSV's
reviewsDF = pd.DataFrame(reviews)
reviewsDF = reviewsDF.astype(str)
entriesDF = pd.DataFrame(entry_list)
entriesDF = entriesDF.astype(str)
reviewsDF.to_csv('reviews.csv', index=False)
entriesDF.to_csv('products.csv', index=False)
