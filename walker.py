import ast
# import file as other


class traceError(Exception):
    pass


def to_set(name, to, op='='):
    if isinstance(name, ast.Name):
        if op == '=':
            ret = '%s = %s\n' % (to_lua(name), to_lua(to))
        else:
            name = to_lua(name)
            ret = '%s = %s %s %s\n' % (name, name, op, to_lua(to))
        return ret
    ret = ''
    for i in zip(name.elts if not isinstance(name, list) else name, to.elts):
        ret += to_set(*i, op=op)
    return ret


def to_lua(tree):
    if isinstance(tree, ast.Module):
        ret = ''
        for i in tree.body:
            ret += to_lua(i)
        return ret
    if isinstance(tree, ast.Assign):
        ret = ''
        if isinstance(tree.targets[0], ast.Tuple):
            ret += to_set(tree.targets[0].elts, tree.value)
        else:
            ret += to_lua(tree.targets[0])
            ret += ' = '
            ret += to_lua(tree.value)
            ret += '\n'
        return ret
    if isinstance(tree, ast.Name):
        return tree.id
    if isinstance(tree, ast.Tuple):
        ret = '{'
        for i in tree.elts:
            ret += to_lua(i) + ', '
        if ret[-2:] == ', ':
            ret = ret[:-2]
        ret += '}'
        return ret
    if isinstance(tree, ast.Call):
        ret = ''
        ret += to_lua(tree.func)
        ret += '('
        for i in tree.args:
            ret += '%s, ' % to_lua(i)
        if ret[-2:] == ', ':
            ret = ret[:-2]
        ret += ')\n'
        return ret
    if isinstance(tree, ast.BinOp):
        opt = tree.op
        if isinstance(opt, ast.Add):
            ret = 'Add('
            ret += to_lua(tree.left)
            ret += ', '
            ret += to_lua(tree.right)
            ret += ')'
            return ret
        if isinstance(opt, ast.Sub):
            op = '-'
        if isinstance(opt, ast.Mult):
            op = '*'
        if isinstance(opt, ast.Div):
            op = '/'
        if isinstance(opt, ast.Mod):
            op = '%'
        ret = '('
        ret += to_lua(tree.left)
        ret += ' %s ' % op
        ret += to_lua(tree.right)
        ret += ')'
        return ret
    if isinstance(tree, ast.Compare):
        opt = tree.ops[0]
        if isinstance(opt, ast.Gt):
            op = '>'
        if isinstance(opt, ast.Lt):
            op = '<'
        if isinstance(opt, ast.GtE):
            op = '>='
        if isinstance(opt, ast.LtE):
            op = '<='
        if isinstance(opt, ast.Eq):
            op = '=='
        if isinstance(opt, ast.NotEq):
            op = '~='
        right = to_lua(tree.comparators[0])
        left = to_lua(tree.left)
        ret = '%s %s %s' % (left, op, right)
        return ret
    if isinstance(tree, ast.AugAssign):
        opt = tree.op
        if isinstance(opt, ast.Add):
            op = '+'
        if isinstance(opt, ast.Sub):
            op = '-'
        if isinstance(opt, ast.Mult):
            op = '*'
        if isinstance(opt, ast.Div):
            op = '/'
        if isinstance(opt, ast.Mod):
            op = '%'
        ret = to_set(tree.target, tree.value, op=op)
        return ret
    if isinstance(tree, ast.If):
        test = to_lua(tree.test)
        hbody = ''
        for i in tree.body:
            hbody += '  '+to_lua(i)
        body = hbody
        ret = 'if %s then\n%send' % (test, body)
        return ret
    if isinstance(tree, ast.Expr):
        return to_lua(tree.value)
    if isinstance(tree, ast.Num):
        return str(tree.n)
    if isinstance(tree, ast.While):
        test = to_lua(tree.test)
        hbody = ''
        for i in tree.body:
            llua = to_lua(i)
            for i in llua.split('\n'):
                hbody += '  '+i+'\n'
        body = hbody
        ret = 'while %s do\n%send\n' % (test, body)
        return ret
    if isinstance(tree, ast.List):
        ret = '{'
        for i in tree.elts:
            ret += '%s, ' % to_lua(i)
        if ret[-2:] == ', ':
            ret = ret[:-2]
        ret += '}'
        return ret
    if isinstance(tree, ast.Subscript):
        ret = ''
        ret += to_lua(tree.value)
        sli = to_lua(tree.slice)
        if sli.isnumeric():
            ret += '[%s]' % (int(sli)+1)
        else:
            ret += '[%s+1]' % sli
        return ret
    if isinstance(tree, ast.Index):
        return to_lua(tree.value)
    if isinstance(tree, ast.Str):
        return '[[%s]]' % tree.s
    if isinstance(tree, ast.For):
        ret = ''
        ret += 'for pl, %s in pairs(' % to_lua(tree.target)
        ret += to_lua(tree.iter)
        ret += ') do\n'
        hbody = ''
        for i in tree.body:
            hbody += '  '+to_lua(i)
        body = hbody
        ret += body
        ret += 'end'
        # print(ret)
        # ret = 'for %s do\n%send\n' % (test, body)
        return ret
    if isinstance(tree, ast.FunctionDef):
        ret = ''
        ret += 'function %s(' % tree.name
        for i in tree.args.args:
            ret += '%s, ' % to_lua(i)
        if ret[-2:] == ', ':
            ret = ret[:-2]
        ret += ')\n'
        hbody = ''
        for i in tree.body:
            llua = to_lua(i)
            for i in llua.split('\n'):
                hbody += '  '+i+'\n'
        body = hbody
        ret += body
        ret += 'end\n'
        return ret
    if isinstance(tree, ast.Pass):
        return ''
    print(tree)
    raise traceError
    exit()


code = open('pre.lua').read()
code += to_lua(ast.parse(open('file.py').read()))
open('exec.lua', 'w').write(code)
