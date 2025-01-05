# Imports -------------------------------------------
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from parsy import (
    generate,
    regex,
    string,
    string_from,
    whitespace,
    forward_declaration,
    Parser,
    seq,
)


# --- AST Node Definitions ---
@dataclass
class EnvVar:
    name: str
    value: str


@dataclass
class Package:
    name: str


@dataclass
class Language:
    name: str
    settings: Dict[str, Union[bool, Dict[str, bool]]]


@dataclass
class Script:
    name: str
    exec_content: str


@dataclass
class NixConfig:
    env: Dict[str, str]
    packages: List[str]
    languages: Dict[str, Language]
    scripts: Dict[str, Script]
    enter_shell: Optional[str]
    enter_test: Optional[str]


# --- Basic Parser Building Blocks ---
space = regex(r"[ \t]")
spaces = space.many()
newline = string("\n")
comment = regex(r"#[^\n]*")
whitespace_or_comment = (spaces | newline | comment).many()

# --- Value Parsers ---
string_content = regex(r'[^"]*')
quoted_string = string('"') >> string_content << string('"')
single_quoted_string = string("''") >> regex(r"[^']*") << string("''")
string_value = quoted_string | single_quoted_string

identifier = regex(r"[A-Za-z_][A-Za-z0-9_]*")
package_ref = seq(
    base=identifier, dot=string(".").optional(), path=identifier.optional()
).combine(lambda base, dot, path: f"{base}{dot or ''}{path or ''}")


# --- Structure Parsers ---
@generate
def env_var():
    name = yield identifier
    yield spaces >> string("=") >> spaces
    value = yield string_value | identifier
    yield string(";").optional() >> whitespace_or_comment
    return EnvVar(name, value)


@generate
def package():
    pkg = yield string("pkgs.") >> identifier
    yield whitespace_or_comment
    return Package(pkg)


@generate
def language_setting():
    name = yield identifier
    yield spaces >> string("=") >> spaces
    value = yield string_from("true", "false").map(lambda x: x == "true")
    yield string(";").optional() >> whitespace_or_comment
    return (name, value)


@generate
def language():
    name = yield identifier
    yield spaces >> string("=") >> spaces >> string("{") >> whitespace_or_comment
    settings = yield language_setting.many()
    yield string("}") >> string(";").optional() >> whitespace_or_comment
    return Language(name, dict(settings))


@generate
def script():
    name = yield identifier
    yield spaces >> string(".exec") >> spaces >> string("=") >> spaces
    content = yield single_quoted_string
    yield string(";").optional() >> whitespace_or_comment
    return Script(name, content)


# --- Main Section Parsers ---
@generate
def env_section():
    yield (
        string("env")
        >> spaces
        >> string("=")
        >> spaces
        >> string("{")
        >> whitespace_or_comment
    )
    vars = yield env_var.many()
    yield string("}") >> string(";").optional() >> whitespace_or_comment
    return {var.name: var.value for var in vars}


@generate
def packages_section():
    yield (
        string("packages")
        >> spaces
        >> string("=")
        >> spaces
        >> string("[")
        >> whitespace_or_comment
    )
    pkgs = yield package.many()
    yield string("]") >> string(";").optional() >> whitespace_or_comment
    return [pkg.name for pkg in pkgs]


@generate
def languages_section():
    yield (
        string("languages")
        >> spaces
        >> string("=")
        >> spaces
        >> string("{")
        >> whitespace_or_comment
    )
    langs = yield language.many()
    yield string("}") >> string(";").optional() >> whitespace_or_comment
    return {lang.name: lang for lang in langs}


@generate
def scripts_section():
    yield (
        string("scripts")
        >> spaces
        >> string("=")
        >> spaces
        >> string("{")
        >> whitespace_or_comment
    )
    scripts_list = yield script.many()
    yield string("}") >> string(";").optional() >> whitespace_or_comment
    return {script.name: script for script in scripts_list}


@generate
def enter_shell_section():
    yield string("enterShell") >> spaces >> string("=") >> spaces
    content = yield single_quoted_string
    yield string(";").optional() >> whitespace_or_comment
    return content


@generate
def enter_test_section():
    yield string("enterTest") >> spaces >> string("=") >> spaces
    content = yield single_quoted_string
    yield string(";").optional() >> whitespace_or_comment
    return content


# --- Complete File Parser ---
@generate
def nix_file():
    yield string("{") >> whitespace_or_comment
    yield string("pkgs, lib, config, inputs, ...")
    yield string("}") >> string(":") >> whitespace_or_comment
    yield string("{") >> whitespace_or_comment

    sections = {}
    while True:
        try:
            if (yield string("}").optional()):
                break

            section = yield (
                env_section.map(lambda x: ("env", x))
                | packages_section.map(lambda x: ("packages", x))
                | languages_section.map(lambda x: ("languages", x))
                | scripts_section.map(lambda x: ("scripts", x))
                | enter_shell_section.map(lambda x: ("enter_shell", x))
                | enter_test_section.map(lambda x: ("enter_test", x))
                | (comment >> whitespace_or_comment).result(None)
            )

            if section is not None:
                name, value = section
                sections[name] = value

        except:
            break

    return NixConfig(
        env=sections.get("env", {}),
        packages=sections.get("packages", []),
        languages=sections.get("languages", {}),
        scripts=sections.get("scripts", {}),
        enter_shell=sections.get("enter_shell"),
        enter_test=sections.get("enter_test"),
    )


# Export the main parser
nix_parser = nix_file
