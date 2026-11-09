p = 'frontend/src/components/admin/admin-sidebar.tsx'
s = open(p).read()
# In TreeRow, replace the Link block with conditional
old_link = '''      <div className="relative">
        <Link
          href={item.href}
          onClick={onNavigate}
          aria-current={active ? "page" : undefined}
          style={{
            paddingLeft: `${indent}px`,
            paddingRight: hasChildren ? "2.5rem" : undefined,
          }}
          className={cn(
            "group relative flex min-h-10 items-center gap-3 rounded-lg text-sm font-medium transition-colors duration-150",
            "before:absolute before:inset-y-2 before:left-0 before:w-0.5 before:rounded-r-full before:transition-colors",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--sidebar-bg)]",
            active
              ? "bg-[var(--sidebar-active-bg)] text-white before:bg-[var(--sidebar-accent)]"
              : "text-white/75 hover:bg-white/[0.07] hover:text-white before:bg-transparent"
          )}
        >
          <Icon
            aria-hidden="true"
            className={cn(
              "h-5 w-5 shrink-0 stroke-[1.7] transition-colors",
              active ? "text-[var(--sidebar-accent)]" : "text-white/65 group-hover:text-white"
            )}
          />
          <span className="min-w-0 truncate">{item.label}</span>
        </Link>'''
new_link = '''      <div className="relative">
        {item.href ? (
        <Link
          href={item.href}
          onClick={onNavigate}
          aria-current={active ? "page" : undefined}
          style={{
            paddingLeft: `${indent}px`,
            paddingRight: hasChildren ? "2.5rem" : undefined,
          }}
          className={cn(
            "group relative flex min-h-10 items-center gap-3 rounded-lg text-sm font-medium transition-colors duration-150",
            "before:absolute before:inset-y-2 before:left-0 before:w-0.5 before:rounded-r-full before:transition-colors",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--sidebar-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--sidebar-bg)]",
            active
              ? "bg-[var(--sidebar-active-bg)] text-white before:bg-[var(--sidebar-accent)]"
              : "text-white/75 hover:bg-white/[0.07] hover:text-white before:bg-transparent"
          )}
        >
          <Icon
            aria-hidden="true"
            className={cn(
              "h-5 w-5 shrink-0 stroke-[1.7] transition-colors",
              active ? "text-[var(--sidebar-accent)]" : "text-white/65 group-hover:text-white"
            )}
          />
          <span className="min-w-0 truncate">{item.label}</span>
        </Link>
        ) : (
        <div
          style={{
            paddingLeft: `${indent}px`,
            paddingRight: hasChildren ? "2.5rem" : undefined,
          }}
          className={cn(
            "group relative flex min-h-10 items-center gap-3 rounded-lg text-sm font-medium text-white/75"
          )}
        >
          <Icon aria-hidden="true" className="h-5 w-5 shrink-0 stroke-[1.7] text-white/65" />
          <span className="min-w-0 truncate">{item.label}</span>
        </div>
        )}'''
assert old_link in s
s = s.replace(old_link, new_link)
# Fix routeIsActive calls with item.href possibly undefined - guard
s = s.replace("const active = routeIsActive(item.href, pathname, searchParams);", "const active = item.href ? routeIsActive(item.href, pathname, searchParams) : false;")
# Fix SidebarLink calls for children - children always have href
s = s.replace('active={routeIsActive(child.href, pathname, searchParams)}', 'active={routeIsActive(child.href!, pathname, searchParams)}')
# Fix item.children possibly undefined in RenderNavItems
s = s.replace("const childActive = item.children.some((child) =>", "const childActive = (item.children || []).some((child) =>")
# Fix classes.map etc not needed
open(p,'w').write(s)
print('done')
