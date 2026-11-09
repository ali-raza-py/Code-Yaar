p = 'frontend/src/app/(admin)/layout.tsx'
s = open(p).read()
old = '    const role = profile?.role || "student";\n    if (![\"admin\", \"administrator\", \"mentor\"].includes(role) && !user.is_staff) {'
new = '    if (user.role !== "administrator") {'
s = s.replace(old, new)
open(p, 'w').write(s)
print('done')
