from urs.utils import Export, Global

class TestExport():
    """
    Testing export functions.
    """

    def test_fix(self):
        name = "/t\\e?s%t*i:n|g<characters>"
        fixed = "_t_e_s_t_i_n_g_characters_"

        assert fixed == Export.NameFile()._fix(name)

    def test_r_category(self):
        assert Export.NameFile()._r_category(None, 0) == Global.categories[5]

        for index, category in enumerate(Global.short_cat[:5]):
            assert Export.NameFile()._r_category(category, 1) == Global.categories[index]

        for i in range(0, len(Global.categories)):
            assert Export.NameFile()._r_category(i, 2) == Global.categories[i]
                
    