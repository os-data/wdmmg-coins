from wdmmg.lib import calculator

constant_tax = (calculator.ni_total + calculator.ct_total) / calculator.population

def test_income_tax():
    def test(i, t):
        ans = calculator.tax_share(i, spending=0) - constant_tax
        assert abs(ans - t) < 1, ans
    # Low incomes
    test(0, 0)
    test(5225, 0)
    # High incomes
    test(2264285.71, 823000)
    test(10e6, 3634700)
    # Mid incomes, requiring interpolation.
    test(25837.04, 3994)

def test_vat():
    ans = calculator.tax_share(0, spending=100) - constant_tax
    assert abs(ans - 17.5) < 1, ans
    ans = calculator.tax_share(100) - constant_tax
    assert abs(ans - 14) < 1, ans

def test_spending_share():
    test_tax = 5000
    ans = calculator.spending_share(test_tax)
    assert 'health' in ans
    assert abs(sum(ans.values()) - test_tax) < 0.01

