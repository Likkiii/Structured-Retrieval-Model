import xml.etree.ElementTree as ET
from prettytable import PrettyTable

# Recursive function to calculate and propagate term frequencies and total terms upward
def calculate_term_frequencies(element, term_frequencies):
    if element.text:
        element_text = element.text.lower()
        for term in query:
            term_frequency = element_text.count(term)
            term_frequencies[element.tag][term] += term_frequency

    total_terms = len(element.text.split())
    term_frequencies[element.tag]["total"] += total_terms

    for child in element:
        calculate_term_frequencies(child, term_frequencies)
        # Propagate child's term frequencies and total terms to the parent
        for term in query:
            term_frequencies[element.tag][term] += term_frequencies[child.tag][term]
        term_frequencies[element.tag]["total"] += term_frequencies[child.tag]["total"]

# Helper function to calculate p(q|element) and p(q|me) for each element
def calculate_element_probabilities(element, term_frequencies, p_q_c):
    p_q_element = [term_frequencies[element.tag][term] / term_frequencies[element.tag]["total"] if term_frequencies[element.tag]["total"] > 0 else 0 for term in query]
    p_q_me = [lamda * p_q_element[i] + (1 - lamda) * p_q_c[i] for i in range(len(query))]
    return p_q_element, p_q_me
  
# Load the XML data from d1.xml
tree = ET.parse("d1.xml")
root = tree.getroot()

# Define the query terms
query = ["chandrayaan", "moon", "lunar"]
# query = ["galaxies", "universe"]

# Define lambda for interpolation
lamda = 0.8

# Initialize term frequencies for each element
term_frequencies = {element.tag: {term: 0 for term in query} for element in root.iter()}
for element in term_frequencies:
    term_frequencies[element]['total'] = 0
    
# Calculate term frequencies for the entire document and propagate upward
calculate_term_frequencies(root, term_frequencies)

# Create a table to store the results
table = PrettyTable()
table.field_names = ["Element", "Length(element)"] + [f"p(q{i + 1}|element)" for i in range(len(query))] + [f"p(q{i + 1}|me)" for i in range(len(query))] + ["p(q|me)"]

# Calculate p(q1|c), p(q2|c), and p(q3|c) for the entire collection
collection_frequencies = {term: 0 for term in query}
for element in root.iter():
    if element.tag.startswith("p"):
        for term in query:
            collection_frequencies[term] += term_frequencies[element.tag][term]
        
total_collection_frequency = sum(collection_frequencies.values())
p_q_c = [collection_frequencies[term] / total_collection_frequency if total_collection_frequency > 0 else 0 for term in query]

# Iterate through the XML tree and calculate probabilities for each element
for element in root.iter():
    p_q_element, p_q_me = calculate_element_probabilities(element, term_frequencies, p_q_c)

    # Calculate p(q|me) as the product of p(qi|me)
    p_q_me_product = 1.0
    for value in p_q_me:
        p_q_me_product *= value
        
    # Format the values to 3 decimal points
    row_values = [element.tag] + [term_frequencies[element.tag]["total"]] + [format(value, '.3f') for value in p_q_element] + [format(value, '.3f') for value in p_q_me] + [format(p_q_me_product, '.6f')]
    table.add_row(row_values)

# Display the table
print("\n--------------------------------------------Structured Text Retrieval Model--------------------------------------------")
print("\nQuery Terms:", query)
print("\nProbability Table:")
print(table)

# Display p(q1|c), p(q2|c), and p(q3|c) for the collection
print("\nProbability for the entire collection (p(qi|c)):")
for i in range(len(query)):
    print(f"p(q{i + 1}|c) = {format(p_q_c[i], '.3f')}")
    
# Create a list to store element information for ranking and sorting
element_info = []

# Iterate through the XML tree and calculate probabilities for each element
for element in root.iter():
    p_q_element, p_q_me = calculate_element_probabilities(element, term_frequencies, p_q_c)

    # Calculate p(q|me) as the product of p(qi|me)
    p_q_me_product = 1.0
    for value in p_q_me:
        p_q_me_product *= value

    # Store element information for ranking and sorting
    element_info.append({
        "Element": element.tag,
        "p(q|me)": p_q_me_product
    })

# Rank the elements based on p(q|me)
element_info.sort(key=lambda x: x["p(q|me)"], reverse=True)

# Create a table with sorted rows based on rank
sorted_table = PrettyTable()
sorted_table.field_names = table.field_names

for info in element_info:
    original_row = next((row for row in table.rows if row[0] == info["Element"]), None)
    sorted_table.add_row(original_row)

# Display the sorted table
print("\nRanked table based on p(q|me):")
print(sorted_table)