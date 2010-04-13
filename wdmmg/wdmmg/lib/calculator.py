income_table = {
    0: 0,
    10000: 2000,
    20000: 5000,
}

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
    disposable_income,
    is_smoker,
    is_driver
):
    '''
    Estimates a person's tax contribution based on the following information:
    
    income - Total personal income. This is used to estimate income tax paid.
    disposable_income - Household expenditure. This is used to estimate VAT paid.
    is_smoker - `True` if the person smokes. This adds a share of tobacco duty.
    is_driver - `True` if the person drives a car. This adds a share of fuel duty.
    '''
    tax = 0.0
    # Income tax: Calculate which income range the income falls in.
    bucket = 0
    for k, v in income_table.items():
        if k <= income and k>bucket:
            bucket = k
    tax += income_table[bucket]
    # NI contributions are divided equally across the population.
    tax += ni_total / population
    # VAT: Multiply disposable income by `vat_rate`.
    tax += disposable_income * vat_rate
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

