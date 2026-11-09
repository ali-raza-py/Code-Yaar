p = 'frontend/src/components/layout/app-sidebar.tsx'
s = open(p).read()
old = '''        <ul className="mt-5 space-y-0.5 border-t border-white/10 pt-3">
          {secondaryItems.map((item) => (
            <SidebarLink
              key={item.label}
              item={item}
              active={routeIsActive(item.href, pathname, searchParams)}
              onNavigate={onNavigate}
            />
          ))}
        </ul>'''
new = '''        <ul className="mt-5 space-y-0.5 border-t border-white/10 pt-3">
          {secondaryItems.map((item) => (
            <SidebarLink
              key={item.label}
              item={item}
              active={routeIsActive(item.href, pathname, searchParams)}
              onNavigate={onNavigate}
            />
          ))}
          {user?.role === "administrator" && (
            <SidebarLink
              item={{ href: "/admin/dashboard", label: "Admin Panel", icon: Settings }}
              active={pathname.startsWith("/admin")}
              onNavigate={onNavigate}
            />
          )}
        </ul>'''
assert old in s, "old not found"
s = s.replace(old, new)
open(p, 'w').write(s)
print('done')
