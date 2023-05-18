from argparse import ArgumentParser
import os
import ast
from typing import Dict, List, Optional, Set
try:
    from plantuml import PlantUML
except ImportError:
    _plantuml = False
else:
    _plantuml = True


class ClassRepresentation:
    
    _classes: Dict[str, "ClassRepresentation"] = {}
    
    def __init__(self, name: str, methods: List[str] = ..., variables: List[str] = ..., bases: List[str] = ..., inner_clses: List["ClassRepresentation"] = ...):
        self.name = name
        self.methods = [] if methods is ... else methods
        self.variables = [] if variables is ... else variables
        self.bases = [] if bases is ... else bases
        self.inner_classes = [] if inner_clses is ... else inner_clses
        
        self._classes[self.name] = self
        
    def __repr__(self) -> str:
        return f"""class {self.name} {{
\t{(chr(10) + chr(9)).join(self.variables)}
\t{(chr(10) + chr(9)).join(self.methods)}
}}
"""
        
        
    def __hash__(self) -> int:
        return hash(self.name)


def create_inheritance_tree(
    ignore: Optional[List[str]] = None,
    output_dir: str = "_structure",
    output_file: str = "diagram.wsd",
    generate_image: bool = True,
    temp_file: bool = False
):
    print(ignore, output_dir, output_file, generate_image, temp_file)
    if ignore is None:
        ignore = []
        
    inheritance_tree = {}
    for dir, dirs, files in os.walk(os.getcwd()):
        if dir.endswith(("__pycache__", *ignore)):
            continue
        
        for file in files:
            if not file.endswith(".py"):
                continue
            
            print("Parse File %r" % file)
            with open(file) as f:
                tree = ast.parse(f.read(), file, mode="exec")
            
            # print(ast.dump(tree, indent=2))
            clses = get_class_from_ast(tree)
            for cls in clses:
                inheritance_tree[cls.name] = set(cls.bases)
    
    if not os.access(output_dir, os.W_OK):
        os.makedirs(output_dir)

    out_path = os.path.join(output_dir, output_file) 

    with open(out_path + ".wsd", "w") as f:
        f.write("@startuml pyGreenfootClsDiagram\n\n")
        for name, cls in ClassRepresentation._classes.items():
            print("Writing class %r" % name)
            f.write(repr(cls) + "\n")
        
        print("Generating arrows")
        f.write(generate_arrows(inheritance_tree))
        f.write("\n@enduml")
        
    print("Successfully generated class diagramm")
    if not _plantuml:
        print("WARNING: Cannot generate image. No plantuml installed.")
        print("WARNING: Install by executin `python -m pip install plantuml`")
        
    elif generate_image:
        pl = PlantUML("http://www.plantuml.com/plantuml/img/")
        print("Generating image using external server...")
        pl.processes_file(out_path + ".wsd", out_path + ".png")
        print("Successfully generated image")
    
    if temp_file:
        os.remove(out_path + ".wsd")
    

        
def generate_arrows(tree: Dict[str, Set[str]]) -> str:
    arrows = ""
    for cls, bases in tree.items():
        for base in bases:
            arrows += f"{base} <|-- {cls}\n"
        arrows += "\n"
    return arrows
            

def get_class_from_ast(ast_module: ast.Module) -> List[ClassRepresentation]:
    res = []
    for ast_node in ast_module.body:
        if isinstance(ast_node, ast.ClassDef):
            res.append(parse_ast_class(ast_node))
            
        # TODO clsmethods
        
    return res


def parse_ast_class(ast_node: ast.ClassDef) -> "ClassRepresentation":
    res = ClassRepresentation(ast_node.name)
    for ast_name in ast_node.bases:
        res.bases.append(ast_name.id)
    
    for ast_body_node in ast_node.body:
        if isinstance(ast_body_node, ast.FunctionDef):
            res.methods.append(get_function_repr(ast_body_node))
            if ast_body_node.name == "__init__":
                res.variables.extend(get_instance_vars(ast_body_node))
    return res


def get_instance_vars(ast_init_func_def: ast.FunctionDef) -> List[str]:
    cls_vars = []
    for stmt in ast_init_func_def.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Attribute):
                    expr = ast.unparse(target)
                    if expr.startswith("self."):
                        cls_vars.append(expr[5:])
                        
        elif isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Attribute):
                expr = ast.unparse(stmt.target)
                if expr.startswith("self."):
                    cls_vars.append(expr[5:] + ": " + ast.unparse(stmt.annotation))
                    
    for i, name in enumerate(cls_vars, start=0):
        if name.startswith("__"):
            cls_vars[i] = "- " + name
        elif name.startswith("_"):
            cls_vars[i] = "~ " + name
        else:
            cls_vars[i] = "+ " + name
    return cls_vars

    

def get_function_repr(ast_func: ast.FunctionDef) -> str:
    r = ""
    name = ast_func.name
    if name.startswith("__"):
        r += "-"
    elif name.startswith("_"):
        r += "~"
    else:
        r += "+"
        
    for decorator in ast_func.decorator_list:
        unparsed = ast.unparse(decorator)
        if unparsed.endswith("method"):
            unparsed = unparsed[:-6]
        r += f" {{{unparsed}}}"
    
    r += " " + name + "("
    args = ast_func.args

    r += ', '.join(get_arg_repr(arg) for arg in args.posonlyargs)
    if args.posonlyargs: 
        r += ", /,"

    r += ', '.join(get_arg_repr(arg) for arg in args.args)
    if args.kwonlyargs:
        if r[-1] != "(":
            r += ", "
        r += "*, " + ', '.join(get_arg_repr(arg) for arg in args.kwonlyargs)

    if args.kwarg:
        r += ", **" + get_arg_repr(args.kwarg)

    r += ")"

    if name != "__init__" and ast_func.returns:
        r += " -> " + ast.unparse(ast_func.returns)

    return r


def get_arg_repr(ast_arg: ast.arg) -> str:
    r = ast_arg.arg
    if ast_arg.annotation:
        r += ": " + ast.unparse(ast_arg.annotation)
    return r
