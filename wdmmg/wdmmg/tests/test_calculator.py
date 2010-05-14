import wdmmg.lib.calculator

calculator = wdmmg.lib.calculator.TaxCalculator2010()

def test_income_tax():
    def test(i, t):
        esttax, explanation = calculator.total_tax(i, spending=0)
        assert abs(esttax - t) < 1, (esttax, t, explanation)
    # Low incomes
    test(0, 2818)
    test(5225, 2818)
    # High incomes
    test(2264285.71, 825818)
    test(10e6, 3637517)
    # Mid incomes, requiring interpolation.
    test(25837.04, 6812)

def test_vat():
    ans = calculator.vat(spending=100)
    assert abs(ans - 17.5) < 1, ans
    ans = calculator.vat(80)
    assert abs(ans - 14) < 1, ans

def test_spending_share():
    test_tax = 5000
    ans = wdmmg.lib.calculator.spending_share(test_tax)
    assert 'health' in ans
    assert abs(sum(ans.values()) - test_tax) < 0.01

