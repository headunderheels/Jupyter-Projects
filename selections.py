
class Selection:
    def __init__(self, sname=""):
        self.name = sname
        self.cuts = {}

    def __str__(self):
        out_str = self.name+":"
        for cut in self.cuts:
            out_str += "\n\t%s [%s,%s]"%(cut,self.cuts[cut]["min"],self.cuts[cut]["max"])
        return out_str

    def addCut(self,var, minval="", maxval="", abs_val=False):
        if var in self.cuts:
            print("Already defined a cut for this variable. Overwriting.")
        self.cuts[var] = {"min": str(minval), "max": str(maxval), "abs_val":abs_val}

    def getCutString(self, index=""):
        cut_str = ""
        for cut in self.cuts:
            minval = self.cuts[cut]["min"]
            maxval = self.cuts[cut]["max"]
            abs_val = self.cuts[cut]["abs_val"]

            varname = cut
            if index != "":
                if "/" in cut:
                    if len(cut.split("/")) > 2:
                        print("Not yet set up to do mutliple division in selector!")
                        exit()
                    num = cut.split("/")[0]
                    den = cut.split("/")[1]
                    varname = "%s[%s]/%s[%s]"%(num, index, den, index)
                else: varname = "%s[%s]"%(cut, index)
            if abs_val: varname = "abs(%s)"%varname

            if minval != "":
                if maxval != "":
                    cut_str += " && (%s < %s && %s > %s)"%(varname,self.cuts[cut]["max"],varname,self.cuts[cut]["min"])
                else:
                    cut_str += " && %s > %s"%(varname,self.cuts[cut]["min"])
            elif maxval != "":
                cut_str += " && %s < %s"%(varname,self.cuts[cut]["max"])
            else: cut_str += " && %s"%varname

        cut_str=cut_str[3:]
        return cut_str

    ########################################################
    # Functions to help with RDataFrames
    ########################################################

    # nSelectedString provides string to use in RDataFrames to define an object count
    # Example usage: counts number of electrons passing selection
    #   e_selection = sel.nSelectedString("electron_pt")
    #   df_edef = dframe.Define("e_n", e_selection)

    def nSelectedString(self, ref_vector):
        selection = '''
            int n = 0;
            for (int i=0; i<%s.size(); i++)
                if (%s) n++;
            return n;'''%(ref_vector, self.getCutString("i"))
        return selection

    # selectedVectorString provides string to use in RDataFrames to get a new vector branch
    # containing only selected objects
    # Example usage: get pt of electrons passing a selection
    #   e_sel_pt = sel.selectedVectorString("electron_pt")
    #   df_ept = dframe.Define("e_pt", e_sel_pt)

    def selectedVectorString(self, ref_vector):
        selection = '''
            auto v = %s;
            v.clear();
            for (int i=0; i<%s.size(); i++)
                if (%s)
                    v.push_back((double)%s[i]);
            return v;'''%(ref_vector, ref_vector, self.getCutString("i"), ref_vector)
        return selection

