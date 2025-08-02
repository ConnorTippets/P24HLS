from dataclasses import dataclass, fields
import typing

from reader import Reader
from writer import Writer

@dataclass()
class staticProp:
    origin : tuple[float, float, float]
    angles : tuple[float, float, float]
    
    prop_type : int
    first_leaf : int
    leaf_count : int
    solid : int
    
    flags : int
    skin : int
    fade_min_dist : float
    fade_max_dist : float
    lighting_origin : tuple[float, float, float]
    
    forced_fade_scale : float
    
    min_dx_level : int
    max_dx_level : int
    
    lightmap_res_x : int
    lightmap_res_y : int
    
    min_cpu_level : int
    max_cpu_level : int
    min_gpu_level : int
    max_gpu_level : int
    
    diffuse_modulation : tuple[int, int, int, int]
    
    disable_x360 : bool
    
    flags_ex : int
    
    uniform_scale : float
    
    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)
    
    def __repr__(self):
        return object.__repr__(self)

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
                self.reader.skip_bytes(3)
            
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
        self.version = version
        self.writer = writer
    
    def write_dict_entries(self, dict_entries : list[str]):
        self.writer.write_int(len(dict_entries))
        
        for entry in dict_entries:
            self.writer.write_bytes(bytes(entry, 'utf-8'))
            self.writer.skip_bytes(128 - len(entry))
    
    def write_leaf_entries(self, leaf_entries : list[int]):
        self.writer.write_int(len(leaf_entries))
        
        for entry in leaf_entries:
            self.writer.write_ushort(entry)
    
    def write_static_props(self, static_props : list[staticProp]):
        self.writer.write_int(len(static_props))
        
        for static_prop in static_props:
            self.writer.write_vector(static_prop.origin)
            self.writer.write_qangle(static_prop.angles)
            
            self.writer.write_ushort(static_prop.prop_type)
            self.writer.write_ushort(static_prop.first_leaf)
            self.writer.write_ushort(static_prop.leaf_count)
            self.writer.write_uchar(static_prop.solid)
            
            if not self.version == 7.1:
                self.writer.write_uchar(static_prop.flags)
            
            self.writer.write_int(static_prop.skin)
            self.writer.write_float(static_prop.fade_min_dist)
            self.writer.write_float(static_prop.fade_max_dist)
            self.writer.write_vector(static_prop.lighting_origin)
            
            if self.version >= 5:
                self.writer.write_float(static_prop.forced_fade_scale)
            
            if self.version in (6, 7, 7.1):
                self.writer.write_ushort(static_prop.min_dx_level)
                self.writer.write_ushort(static_prop.max_dx_level)
            
            if self.version == 7.1:
                self.writer.write_uint(static_prop.flags)
                self.writer.write_ushort(static_prop.lightmap_res_x)
                self.writer.write_ushort(static_prop.lightmap_res_y)
            
            if self.version >= 8 and self.version != 7.1:
                self.writer.write_uchar(static_prop.min_cpu_level)
                self.writer.write_uchar(static_prop.max_cpu_level)
                self.writer.write_uchar(static_prop.min_gpu_level)
                self.writer.write_uchar(static_prop.max_gpu_level)
            
            if self.version >= 7:
                self.writer.write_color32(static_prop.diffuse_modulation)
            
            if self.version in (9, 10):
                self.writer.write_bool(static_prop.disable_x360)
                self.writer.skip_bytes(3)
            
            if self.version >= 10:
                self.writer.write_uint(static_prop.flags_ex)
            
            if self.version >= 11:
                self.writer.write_float(static_prop.uniform_scale)
    
    def write(self, sprp : SPRP):
        self.write_dict_entries(sprp.dict_entries)
        self.write_leaf_entries(sprp.leaf_entries)
        self.write_static_props(sprp.static_props)

class StaticPropsGameLumpConverter:
    def __init__(self, reader : Reader, writer : Writer, current_version : int, new_version : int):
        self.reader = StaticPropsGameLumpReader(current_version, reader)
        self.writer = StaticPropsGameLumpWriter(new_version,     writer)
        self.current_version = current_version
        self.new_version = new_version
    
    def convert(self):
        sprp = self.reader.read()
        self.writer.write(sprp)