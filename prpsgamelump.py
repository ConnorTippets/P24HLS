from dataclasses import dataclass
import typing

from reader import Reader
from writer import Writer

class staticProp:
    def __init__(self, **kwargs : dict):
        for k, v in kwargs.items():
            setattr(self, k, v)

@dataclass
class SPRP:
    dict_entries : list[str]
    leaf_entries : list[int]
    static_props : list[staticProp]

class StaticPropsGameLumpReader:
    def __init__(self, version : int, reader : Reader):
        self.version = version
        self.reader = reader
    
    def read_dict_entries(self) -> list[str]:
        entry_count = self.reader.read_int()
        
        dict_entries = []
        for _ in range(entry_count):
            raw = self.reader.read_bytes(128)
            entry = raw.replace(b'\x00', b'').decode()
            
            dict_entries.append(entry)
        
        return dict_entries
    
    def read_leaf_entries(self) -> list[int]:
        entry_count = self.reader.read_int()
        
        leaf_entries = []
        for _ in range(entry_count):
            leaf_entries.append(self.reader.read_ushort())
        
        return leaf_entries

    def read_static_props(self) -> list[staticProp]:
        count = self.reader.read_int()
        
        static_props = []
        for _ in range(count):
            output : dict[str, typing.Any] = {}
            
            output['origin'] = self.reader.read_vector()
            output['angles'] = self.reader.read_qangle()
            
            output['prop_type'] = self.reader.read_ushort()
            output['first_leaf'] = self.reader.read_ushort()
            output['leaf_count'] = self.reader.read_ushort()
            output['solid'] = self.reader.read_uchar()
            
            if not self.version == 7.1:
                output['flags'] = self.reader.read_uchar()
            
            output['skin'] = self.reader.read_int()
            output['fade_min_dist'] = self.reader.read_float()
            output['fade_max_dist'] = self.reader.read_float()
            output['lighting_origin'] = self.reader.read_vector()
            
            if self.version >= 5:
                output['forced_fade_scale'] = self.reader.read_float()
            
            if self.version in (6, 7, 7.1):
                output['min_dx_level'] = self.reader.read_ushort()
                output['max_dx_level'] = self.reader.read_ushort()
            
            if self.version == 7.1:
                output['flags'] = self.reader.read_uint()
                output['lightmap_res_x'] = self.reader.read_ushort()
                output['lightmap_res_y'] = self.reader.read_ushort()
            
            if self.version >= 8:
                output['min_cpu_level'] = self.reader.read_uchar()
                output['max_cpu_level'] = self.reader.read_uchar()
                output['min_gpu_level'] = self.reader.read_uchar()
                output['max_gpu_level'] = self.reader.read_uchar()
            
            if self.version >= 7 and self.version != 7.1:
                output['diffuse_modulation'] = self.reader.read_color32()

            if self.version in (9, 10):
                output['disable_x360'] = self.reader.read_bool()
            
            if self.version >= 10:
                output['flags_ex'] = self.reader.read_uint()
            
            if self.version >= 11:
                output['uniform_scale'] = self.reader.read_float()
            
            static_props.append(staticProp(**output))
        
        return static_props
    
    def read(self) -> SPRP:
        dict_entries = self.read_dict_entries()
        leaf_entries = self.read_leaf_entries()
        static_props = self.read_static_props()
        
        return SPRP(dict_entries, leaf_entries, static_props)

class StaticPropsGameLumpWriter:
    def __init__(self, version : int, writer : Writer):
        ...
    
    def write(self, sprp : SPRP):
        ...

class StaticPropsGameLumpConverter:
    def __init__(self, reader : Reader, writer : Writer, current_version : int, new_version : int):
        self.reader = StaticPropsGameLumpReader(current_version, reader)
        self.writer = StaticPropsGameLumpWriter(new_version,     writer)
        self.current_version = current_version
        self.new_version = new_version
    
    def convert(self):
        sprp = self.reader.read()
        print(sprp)
        
        self.writer.write(sprp)