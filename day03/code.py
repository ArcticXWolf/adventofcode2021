import sys
import logging

logging.basicConfig(format="%(message)s", level=logging.INFO)

bits = []
numbers = []
with open(sys.argv[1], "r") as f:
    for line in f.readlines():
        line = line.strip()
        numbers.append(int(line, 2))
        for index, bit in enumerate([char for char in line]):
            if index >= len(bits):
                bits.append([])
            bits[index].append(bit)

logging.debug(f"Bitlist: {bits}")
logging.debug(f"Numbers: {numbers}")

result = ""
for bitlist in bits:
    most_common_element = max(set(bitlist), key=bitlist.count)
    result = f"{result}{most_common_element}"

gammarate = int(result, 2)
epsilonrate = (1 << (len(bits))) - 1 - gammarate
logging.info(f"Gammarate: {gammarate}")
logging.info(f"Epsilonrate: {epsilonrate}")
logging.info(f"Multipilcation: {gammarate * epsilonrate}")

o2_numbers = list(range(len(numbers)))
co2_numbers = list(range(len(numbers)))
logging.debug(f"O2: {o2_numbers}")
logging.debug(f"CO2: {co2_numbers}")

for search_index, bitlist in enumerate(bits):
    if len(o2_numbers) > 1:
        filtered_bitlist = [x for i, x in enumerate(bitlist) if i in o2_numbers]
        zero_count = filtered_bitlist.count("0")
        one_count = filtered_bitlist.count("1")

        deletion_criteria = "1"
        if zero_count > one_count:
            deletion_criteria = "0"

        deletion_indices = [i for i, x in enumerate(bitlist) if x != deletion_criteria]
        for deletion_index in deletion_indices:
            try:
                o2_numbers.remove(deletion_index)
            except:
                pass
        logging.debug(
            f"O2 Counts: {zero_count}/{one_count} Bitcriteria: {deletion_criteria}, remove {deletion_indices}, remaining {o2_numbers}"
        )

for search_index, bitlist in enumerate(bits):
    if len(co2_numbers) > 1:
        filtered_bitlist = [x for i, x in enumerate(bitlist) if i in co2_numbers]
        zero_count = filtered_bitlist.count("0")
        one_count = filtered_bitlist.count("1")

        deletion_criteria = "0"
        if zero_count > one_count:
            deletion_criteria = "1"

        deletion_indices = [i for i, x in enumerate(bitlist) if x != deletion_criteria]
        for deletion_index in deletion_indices:
            try:
                co2_numbers.remove(deletion_index)
            except:
                pass
        logging.debug(
            f"CO2 Counts: {zero_count}/{one_count} Bitcriteria: {deletion_criteria}, remove {deletion_indices}, remaining {co2_numbers}"
        )

logging.info(f"O2: {numbers[o2_numbers[0]]}")
logging.info(f"CO2: {numbers[co2_numbers[0]]}")
logging.info(f"Multiplication: {numbers[o2_numbers[0]] * numbers[co2_numbers[0]]}")
