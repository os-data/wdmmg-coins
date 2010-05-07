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
    is_smoker = None,
    is_driver = None
):
    '''
    Estimates a person's tax contribution based on the following information:
    
    income - Total personal income. This is used to estimate income tax paid.
    spending - Household expenditure. This is used to estimate VAT paid.
    is_smoker - `True` if the person smokes, or `False` if not. If specified,
      this adds or removes a share of tobacco duty.
    is_driver - `True` if the person drives a car, or `False` if not. If
      specified, this adds or removes a share of fuel duty.
    
    Returns a pair `(tax, explanation)`. The `explanation` is a list of strings
    describing the steps of the calculation.
    '''
    tax, explanation = 0.0, []
    # Income tax: Calculate which income range the income falls in.
    lower = (0.0, 0.0)
    for upper in income_table:
        if upper[0] >= income:
            # Found the right band. Use linear interpolation.
            for band in [lower, upper]:
                explanation.append('''\
There is an income band in which the national average income is %.2f and the \
national average income tax paid is %.2f.''' % band)
            income_tax = lower[1] + (income-lower[0]) * (upper[1]-lower[1]) / (upper[0]-lower[0])
            break
        else:
            lower = upper
    else:
        # Above all the bands. Use constant tax rate.
        explanation.append('''\
For very high earners, the national average fraction of income paid as income \
tax is %.1f%%.''' % (income_top_rate*100))
        income_tax = income * income_top_rate
    explanation.append('''\
Therefore, a person with an income of %.2f pays roughly %.2f in income tax.\
''' % (income, income_tax))
    tax += income_tax
    # NI contributions are divided equally across the population.
    ni = ni_total / population
    explanation.append('''\
The total National Insurance paid by the whole population is %.0f. This is very \
roughly equally shared between %d people. Each person's share is %.2f.\
''' % (ni_total, population, ni))
    tax += ni
    # VAT.
    if spending is None:
        spending = income * 0.8
        explanation.append('''\
A person with an income of %.2f probably spends about %.2f on goods and \
services.''' % (income, spending))
    vat = spending * vat_rate
    explanation.append('''\
A person with expenditure of %.2f probably pays about %.2f in VAT.\
''' % (spending, vat))
    tax += vat
    # Corporation tax is divided equally across the population.
    ct = ct_total / population
    explanation.append('''\
The total Corporation Tax paid by all UK companies is %.0f. It is difficult to \
define a person's individual share. The simplest approach is to share it \
equally between %d people. Each person's share is then %.2f.\
''' % (ct_total, population, ct))
    tax += ct
    # Fuel duty.
    if is_driver is None:
        fuel_duty = fuel_total / population
        explanation.append('''\
The total Fuel Duty paid by the whole population is %f. Without knowing who is \
a driver, the best approach is to share it equally between all %d people. Each \
person's share is %.2f.\
''' % (fuel_total, population, fuel_duty))
    elif is_driver:
        fuel_duty = fuel_total / fuel_population
        explanation.append('''\
The total Fuel Duty paid by the whole population is %f. This is very \
roughly equally shared between %d drivers. Each driver's share is %.2f.\
''' % (fuel_total, fuel_population, fuel_duty))
    else:
        fuel_duty = 0
    tax += fuel_duty
    # Tobacco duty.
    if is_smoker is None:
        tobacco_duty = tobacco_total / population
        explanation.append('''\
The total Tobacco Duty paid by the whole population is %f. Without knowing who \
is a smoker, the best approach is to share it equally between all %d people. \
Each person's share is %.2f.\
''' % (fuel_total, population, fuel_duty))
    elif is_smoker:
        tobacco_duty = tobacco_total / tobacco_population
        explanation.append('''\
The total Tobacco Duty paid by the whole population is %f. This is very \
roughly equally shared between %d smokers. Each smoker's share is %.2f.\
''' % (tobacco_total, tobacco_population, tobacco_duty))
    else:
        tobacco_duty = 0
    tax += tobacco_duty
    return tax, explanation

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

