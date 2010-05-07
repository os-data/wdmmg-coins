import csv
from StringIO import StringIO

# National statistics for income bands.
# In each band, column 1 is the average income, and column 2 is the average tax.
# This comes from table 2-5 of http://www.hmrc.gov.uk/stats/income_tax/menu.htm .
# We use the 2007-08 data, which is the latest year surveyed.
# Columns 0, 1, 2 and 4 are from the source data.
# Column 3 is the ratio of column 1 to column 2.
# We map from column 3 to column 4.
# We connect the data points by linear interpolation.
# We add a data point for the tax-free personal allowance.
# For very high incomes, we use a constant tax/income ratio.
reader = csv.reader(StringIO('''\
"Low income","total income","count","average income","tax"
5225,14700000000,2290000,6419.21,111
7500,29800000000,3400000,8764.71,378
10000,82200000000,6600000,12454.55,1110
15000,94600000000,5430000,17421.73,2200
20000,168000000000,6850000,24525.55,3720
30000,201000000000,5340000,37640.45,6460
50000,125000000000,1900000,65789.47,16200
100000,39600000000,328000,120731.71,36000
150000,21900000000,128000,171093.75,54500
200000,43100000000,149000,289261.74,96300
500000,19200000000,28000,685714.29,235000
1000000,31700000000,14000,2264285.71,823000
'''))
headings = reader.next()
income_table = list(reader)
income_table = (
    [(income_table[0][0], 0)] + # Tax-free personal allowance.
    [(row[3], row[4]) for row in income_table] # Columns 3 and 4.
)
income_table = [(float(income), float(tax)) for income, tax in income_table]
income_top_rate = income_table[-1][1] / income_table[-1][0] # For very high incomes.

vat_rate = 0.175
population = 61.0e6
ni_total = 98.0e9
ct_total = 41.8e9
fuel_total = 24.7e9
fuel_population = population * 0.77
tobacco_total = 7.9e9
tobacco_population = population * 0.21

def tax_share(
    income,
    spending = None,
    is_smoker = False,
    is_driver = False
):
    '''
    Estimates a person's tax contribution based on the following information:
    
    income - Total personal income. This is used to estimate income tax paid.
    spending - Household expenditure. This is used to estimate VAT paid.
    is_smoker - `True` if the person smokes. This adds a share of tobacco duty.
    is_driver - `True` if the person drives a car. This adds a share of fuel duty.
    '''
    tax = 0.0
    # Income tax: Calculate which income range the income falls in.
    lower = (0.0, 0.0)
    for upper in income_table:
        if upper[0] >= income:
            # Found the right band. Use linear interpolation.
            income_tax = lower[1] + (income-lower[0]) * (upper[1]-lower[1]) / (upper[0]-lower[0])
            break
        else:
            lower = upper
    else:
        # Above all the bands. Use constant tax rate.
        income_tax = income * income_top_rate
    tax += income_tax
    # NI contributions are divided equally across the population.
    tax += ni_total / population
    # VAT: Multiply spending by `vat_rate`.
    if spending is None:
        # Estimate based on income.
        spending = income * 0.8
    tax += spending * vat_rate
    # Corporation tax is divided equally across the population.
    tax += ct_total / population
    # Fuel duty: if a driver, fuel duty is divided equally across drivers.
    if is_driver:
        tax += fuel_total / fuel_population
    # Tobacco duty: if a smoker, tobacco duty is divided equally across smokers.
    if is_smoker:
        tax += tobacco_total / tobacco_population
    return tax

spending_table = {
    'social_protection': 301e9,
    'health': 110e9,
    'education': 82e9,
}

spending_total = sum([v for v in spending_table.values()])

def spending_share(tax):
    '''
    Calculates a person's share of public spending, given their tax contribution.
    Returns a dict from top-level COFOG function to money.
    '''
    return dict([(k, tax * v / spending_total) for k, v in spending_table.items()])

