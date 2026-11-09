p = 'frontend/src/components/admin/admin-sidebar.tsx'
s = open(p).read()
s = s.replace("interface NavItem {\n  href: string;", "interface NavItem {\n  href?: string;")
s = s.replace("  Home,\n", "  Home,\n  LogOut,\n")
s = s.replace('  const { user, profile, signOut } = useAuth();\n  const displayName = user?.first_name || user?.username || "Admin";',
              '  const { user, profile, signOut } = useAuth();\n  const displayName = user?.first_name || user?.username || "Admin";\n  const userRole = profile?.role || "student";')
s = s.replace("const hasChildren = item.children && item.children.length > 0;", "const hasChildren = Boolean(item.children && item.children.length > 0);")
open(p, 'w').write(s)
print('done')
