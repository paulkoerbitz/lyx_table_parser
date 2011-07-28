#!/usr/bin/env python
"""Produces a .tex file from a .lyx document containing a table"""
import re
import os

def lyx2tex(lyx_filename):
    """Converts a lyx to a tex file, throws runtime error if
    conversion fails."""
    if os.system('lyx --export latex %s' % lyx_filename) or\
            not os.path.isfile(lyx_filename.replace('.lyx','.tex')):
        raise RuntimeError("'lyx --export latex' failed for file %s" 
                           % lyx_filename)


def extract_tex_environment(lines, regex_env):
    """returns a list of strings that make up the first environment of
    type matched by regex_env in lines and lines (iterated to the end
    of the environment).  Beginning and end of environment are assumed
    to be on their own lines. If no environment is matched
    extracted_env is returned empty and lines is iterated through to
    the end. If the environment is not closed (e.g. \begin{tabluar}
    without \end{tabular} a RuntimeError is raised"""
    extracted_env = []    
    line = lines.next()
    open_env = False
    for line in lines:
        if re.match("\\s*\\\\begin{(%s)}.*" % regex_env, line): 
            open_env = True
            extracted_env.append(line)
            matched_env = re.match("\\s*\\\\begin{(%s)}.*" 
                                   % regex_env, line).group(1)
            break

    if open_env:
        for line in lines:
            extracted_env.append(line)
            match = re.match("\\s*\\\\end{(%s)}.*" % regex_env, line)
            if match and match.group(1) == matched_env:
                open_env = False
                break
        if open_env:
            raise RuntimeError(("Unbalanced environment %s, \\begin{%s}"\
                                   + " was found but \\end{%s} was not.")
                               % ((matched_env,)*3))
                
    return extracted_env, lines


def crop_file_to_tex_table(tex_filename):
    """Extracts the first table in tex_filename. Overwrites the input file"""
    lines = open(tex_filename)
    table, _ = extract_tex_environment(lines, "tabular[*a-z]?|sideways")
    lines.close()
    outfile = open(tex_filename,'w')
    for line in table:
        outfile.write(line)
    outfile.close()
        
    
def tex_tables_from_lyx_files(lyxfiles):
    """converts lyx to tex files and crops them to the first table"""
    print(lyxfiles)
    for lyxfile in lyxfiles:
        try:
            lyx2tex(lyxfile)
            crop_file_to_tex_table(lyxfile.replace('lyx','tex'))
        except RuntimeError as error:
            print(error.message)


if __name__ == '__main__':
    import sys
    tex_tables_from_lyx_files(
        [f for f in sys.argv if re.match("[-_a-z]+\.lyx",f)])
