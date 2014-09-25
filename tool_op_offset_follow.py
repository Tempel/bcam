import math
from tool_operation import ToolOperation, TOEnum
from tool_abstract_follow import TOAbstractFollow
from generalized_setting import TOSetting
from calc_utils import find_vect_normal, mk_vect, normalize, vect_sum, vect_len
from elements import ELine, EArc, ECircle

import cairo
import json

class TOOffsetFollow(TOAbstractFollow):
    def __init__(self, state, depth=0, index=0, offset=0, data=None):
        super(TOAbstractFollow, self).__init__(state)
        self.state = state
        self.name = TOEnum.offset_follow
        if data == None:
            self.index = index
            self.depth = depth
            self.offset = 0
            self.path = None
            self.offset_path = None
        else:
            self.deserialize(data)

        self.display_name = TOEnum.offset_follow+" "+str(self.index)

    def serialize(self):
        return {'type': 'tooffsetfollow', 'path_ref': self.path.name, 'depth': self.depth, 'index': self.index, 'offset': self.offset}

    def deserialize(self, data):
        self.depth = data["depth"]
        self.index = data["index"]
        self.offset = data["offset"]

        p = self.try_load_path_by_name(data["path_ref"], self.state)
        if p:
            self.apply(p)

    def get_settings_list(self):
        settings_lst = [TOSetting("float", 0, self.state.settings.material.thickness, self.depth, "Depth, mm: ", self.set_depth_s),
                        TOSetting("float", None, None, 0, "Offset, mm: ", self.set_offset_s)]
        return settings_lst

    def set_depth_s(self, setting):
        self.depth = setting.new_value

    def set_offset_s(self, setting):
        self.offset = setting.new_value
        self.__build_offset_path(self.path)
        self.draw_list = self.offset_path
        
    def __build_offset_path(self, p):
        new_elements = []
        elements = p.get_ordered_elements()
        if len(elements)==0:
            return False
        if len(elements)==1:
            e = elements[0]
            if type(e).__name__ == "ECircle":
                new_elements.append(ECircle(e.center, e.radius+self.offset, e.lt, None))
            else:
                return
        else:
            s = elements[0].start
            e = elements[0].end
            nsn = elements[0].get_normalized_start_normal()
            s_pt = [nsn[0]*self.offset+s[0], nsn[1]*self.offset+s[1], 0]
            for i, e in enumerate(elements):
                sc = e.start # current start
                ec = e.end # current end


                if s_pt == None:
                    nsn = e.get_normalized_start_normal()
                    n = normalize(vect_sum(nsn, nen)) # sum of new start normal and prev end normal
                    shift = sc
                    s_pt = [n[0]*self.offset+shift[0], n[1]*self.offset+shift[1], 0]

                if i<len(elements)-1:
                    nnsn = elements[i+1].get_normalized_start_normal()
                    nen = e.get_normalized_end_normal()
                    n = vect_sum(nnsn, nen) # sum of next start normal and current end normal
                    shift = ec
                    e_pt = [n[0]*self.offset+shift[0], n[1]*self.offset+shift[1], 0]
                else:
                    nen = e.get_normalized_end_normal()
                    n = nen
                    shift = ec
                    e_pt = [n[0]*self.offset+shift[0], n[1]*self.offset+shift[1], 0]
                if type(e).__name__ == "ELine":
                    ne = ELine(s_pt, e_pt, e.lt)
                elif type(e).__name__ == "EArc":
                    ne = EArc(center=e.center, lt=e.lt, start=s_pt, end=e_pt)

                new_elements.append(ne)
                s_pt = None
                e_pt = None
        self.offset_path = new_elements
        
    def apply(self, path):
        if path.operations[self.name]:
            if path.ordered_elements!=None:
                self.path = path
                self.__build_offset_path(path)
                self.draw_list = self.offset_path
                return True
        return False

    def get_gcode(self):
        cp = self.tool.current_position
        out = ""
        new_pos = [cp[0], cp[1], self.tool.default_height]
        out+= self.state.settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        start = self.offset_path[0].start

        new_pos = [start[0], start[1], new_pos[2]]
        out+= self.state.settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos

        for step in range(int(self.depth/(self.tool.diameter/2.0))+1):
            for e in self.offset_path:
                out += self.process_el_to_gcode(e, step)

        new_pos = [new_pos[0], new_pos[1], self.tool.default_height]
        out+= self.state.settings.default_pp.move_to_rapid(new_pos)
        self.tool.current_position = new_pos
        return out

    def __repr__(self):
        return "<Exact follow>"
