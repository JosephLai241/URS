from urs.utils import Export, Global

class TestExport():
    """
    Testing export functions. Function names are pretty self-explanatory, so I 
    will not be adding comments above the functions.
    """

    def test_fix(self):
        name = "/t\\e?s%t*i:n|g<characters>"
        fixed = "_t_e_s_t_i_n_g_characters_"

        assert fixed == Export.NameFile()._fix(name)

    def test_r_category_first_switch(self):
        assert Export.NameFile()._r_category(None, 0) == Global.categories[5]

    def test_r_category_second_switch(self):
        for index, category in enumerate(Global.short_cat[:5]):
            assert Export.NameFile()._r_category(category, 1) == Global.categories[index]

    def test_r_category_third_switch(self):
        for i in range(0, len(Global.categories)):
            assert Export.NameFile()._r_category(i, 2) == Global.categories[i]
                
    