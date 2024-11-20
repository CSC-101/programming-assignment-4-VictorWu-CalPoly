import sys
import os
import build_data

import county_demographics
from build_data import convert_county

#Each operation
def population_total(counties):
    total = 0
    for county in counties:                             #counties will update per filter
        total += county.population['2014 Population']
    print(f"2014 Population: {total}")
    return total


def display(counties):
    for county in counties:
        print(f"{county.county}, {county.state}")
        print(f"\tPopulation: {county.population.get('2014 Population', 'N/A')}")
        print("\tAge:")
        print(f"\t\t< 5: {county.age.get('Percent Under 5 Years', 'N/A')}%")
        print(f"\t\t< 18: {county.age.get('Percent Under 18 Years', 'N/A')}%")
        print(f"\t\t> 65: {county.age.get('Percent 65 and Older', 'N/A')}%")
        print("\tEducation")
        print(f"\t\t>= High School: {county.education.get('High School or Higher', 'N/A')}%")
        print(f"\t\t>= Bachelor's: {county.education.get('Bachelor\'s Degree or Higher', 'N/A')}%")
        print("\tEthnicity Percentages")
        print(
            f"\t\tAmerican Indian and Alaska Native: {county.ethnicities.get('American Indian and Alaska Native Alone', 'N/A')}%")
        print(f"\t\tAsian Alone: {county.ethnicities.get('Asian Alone', 'N/A')}%")
        print(f"\t\tBlack Alone: {county.ethnicities.get('Black Alone', 'N/A')}%")
        print(f"\t\tHispanic or Latino: {county.ethnicities.get('Hispanic or Latino', 'N/A')}%")
        print(
            f"\t\tNative Hawaiian and Other Pacific Islander Alone: {county.ethnicities.get('Native Hawaiian and Other Pacific Islander Alone', 'N/A')}%")
        print(f"\t\tTwo or More Races: {county.ethnicities.get('Two or More Races', 'N/A')}%")
        print(f"\t\tWhite Alone: {county.ethnicities.get('White Alone', 'N/A')}%")
        print(
            f"\t\tWhite Alone, not Hispanic or Latino: {county.ethnicities.get('White Alone, not Hispanic or Latino', 'N/A')}%")
        print("\tIncome")
        print(f"\t\tMedian Household: {county.income.get('Median Household Income', 'N/A')}")
        print(f"\t\tPer Capita: {county.income.get('Per Capita Income', 'N/A')}")
        print(f"\t\tBelow Poverty Level: {county.income.get('Persons Below Poverty Level', 'N/A')}%")
        print()


def filter_state(counties, state:str):
    filtered = []
    for county in counties:
        if county.state == state:
            filtered.append(county)
    print(f"Filter: state == {state} ({len(filtered)} entries)")
    return filtered


def filter_gt(counties, field:str, threshold:float):
    field_parts = field.split('.')
    category = field_parts[0]
    subcategory = field_parts[1]
    filtered = []
    for county in counties:
        try:
            if category == "Education":
                number = county.education.get(subcategory)
            elif category == "Ethnicities":
                number = county.ethnicities.get(subcategory)
            elif category == "Income":
                number = county.income.get(subcategory)
            else:
                raise ValueError(f"Unknown category: {category}")

            if number is not None and number > threshold:
                filtered.append(county)

        except AttributeError:
            print(f"County {county.name} does not have the required '{category} structure")

    count = len(filtered)
    print(f"Filter: {field} < {threshold} ({count} entries)")
    return filtered


def filter_lt(counties, field:str, threshold:float):
    field_parts = field.split('.')
    category = field_parts[0]
    subcategory = field_parts[1]
    filtered = []
    for county in counties:
        try:
            if category == "Education":
                number = county.education.get(subcategory)
            elif category == "Ethnicities":
                number = county.ethnicities.get(subcategory)
            elif category == "Income":
                number = county.income.get(subcategory)
            else:
                raise ValueError(f"Unknown category: {category}")

            if number is not None and number < threshold:
                filtered.append(county)

        except AttributeError:
            print(f"County {county.name} does not have the required '{category} structure")

    count = len(filtered)
    print(f"Filter: {field} < {threshold} ({count} entries)")
    return filtered


def population(counties, field:str):
    population_count = 0
    field_parts = field.split('.')
    category = field_parts[0]
    subcategory = field_parts[1]

    for county in counties:
        try:
            if category == "Education":
                percentage = county.education.get(subcategory)
            elif category == "Ethnicities":
                percentage = county.ethnicities.get(subcategory)
            elif category == "Income":
                percentage = county.income.get(subcategory)
            else:
                raise ValueError(f"Unknown category: {category}")

            if percentage is not None:
                population_count += county.population['2014 Population'] * (percentage / 100)
            else:
                print(f"Field '{field}' not found in the county data")

        except AttributeError:
            print(f"County {county.name} does not have the required '{category} structure")
    print(f"2014 {field} population:{population_count}")
    return population_count


def percent(counties, field:str):
    sub_population = 0
    total_population = 0
    sub_population_percentage = 0
    field_parts = field.split('.')
    category = field_parts[0]
    subcategory = field_parts[1]

    for county in counties:
        try:
            if category == "Education":
                percentage = county.education.get(subcategory)
            elif category == "Ethnicities":
                percentage = county.ethnicities.get(subcategory)
            elif category == "Income":
                percentage = county.income.get(subcategory)
            else:
                raise ValueError(f"Unknown category: {category}")

            if percentage is not None:
                total_population += county.population['2014 Population']
                sub_population += county.population['2014 Population'] * (percentage / 100)
            else:
                print(f"Field '{field}' not found in the county data")

        except AttributeError:
            print(f"County {county.name} does not have the required '{category} structure")

    if total_population > 0:
        sub_population_percentage = (sub_population / total_population) * 100
        print(f"2014 {field} percentage:{sub_population_percentage:}")
    else:
        print("Total population is zero, cannot calculate")

    return sub_population_percentage


def operation():
    filename = sys.argv[1]
    try:
        counties = build_data.get_data()  #access the full data set by converting unreadable data to readable
        filepath = os.path.join('inputs', filename)
        with open(filepath, 'r') as infile:   #Automatically closes file
            for line in infile:
                line = line.strip()    #removes whitespaces

                if "filter-state" in line:
                    state = line.split(":")[1]
                    counties = filter_state(counties, state)

                elif "filter-gt" in line:
                    try:
                        field = line.split(":")[1]
                        value = line.split(":")[2]
                        counties = filter_gt(counties, field, float(value))
                    except ValueError:
                        print("Data cannot be converted to float value")


                elif "filter-lt" in line:
                    try:
                        field = line.split(":")[1]
                        value = line.split(":")[2]
                        counties = filter_lt(counties, field, float(value))
                    except ValueError:
                        print("Data cannot be converted to float value")


                elif "population" in line and ":" in line:
                    field = line.split(":")[1]
                    population(counties, field)

                elif "percent" in line:
                    field = line.split(":")[1]
                    percent(counties, field)

                elif "population-total" in line:
                    population_total(counties)

                elif "display" in line:
                    display(counties)

    except FileNotFoundError:
        print("Error File Not Found")

    print("End of Program")

if __name__ == "__main__":
    operation()