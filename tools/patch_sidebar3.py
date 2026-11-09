p = 'frontend/src/components/admin/admin-sidebar.tsx'
s = open(p).read()
old = '''      {filteredItems.map((item) => {
        const active = item.href ? routeIsActive(item.href, pathname, searchParams) : false;
        const hasChildren = Boolean(item.children && item.children.length > 0);

        if (hasChildren) {
          const [expanded, setExpanded] = useState(false);
          const childActive = (item.children || []).some((child) =>
            routeIsActive(child.href!, pathname, searchParams)
          );
          const activeDescendant = childActive && !expanded;

          return (
            <TreeRow
              key={item.label}
              item={item}
              active={active}
              depth={depth}
              hasChildren
              expanded={expanded}
              onToggle={() => setExpanded(!expanded)}
              activeDescendant={activeDescendant}
              onNavigate={onNavigate}
            >
              {item.children!.map((child) => (
                <SidebarLink
                  key={child.href}
                  item={child}
                  active={routeIsActive(child.href!, pathname, searchParams)}
                  onNavigate={onNavigate}
                />
              ))}
            </TreeRow>
          );
        }

        return (
          <SidebarLink
            key={item.href}
            item={item}
            active={active}
            onNavigate={onNavigate}
          />
        );
      })}'''
new = '''      {filteredItems.map((item) => {
        const active = item.href ? routeIsActive(item.href, pathname, searchParams) : false;
        const hasChildren = Boolean(item.children && item.children.length > 0);

        if (hasChildren) {
          return (
            <ExpandableNavItem
              key={item.label}
              item={item}
              active={active}
              depth={depth}
              pathname={pathname}
              searchParams={searchParams}
              onNavigate={onNavigate}
            />
          );
        }

        return (
          <SidebarLink
            key={item.href}
            item={item}
            active={active}
            onNavigate={onNavigate}
          />
        );
      })}'''
assert old in s
s = s.replace(old, new)
# Add ExpandableNavItem component before RenderNavItems
comp = '''function ExpandableNavItem({
  item,
  active,
  depth,
  pathname,
  searchParams,
  onNavigate,
}: {
  item: NavItem;
  active: boolean;
  depth: number;
  pathname: string;
  searchParams: URLSearchParams;
  onNavigate: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const childActive = (item.children || []).some((child) =>
    routeIsActive(child.href!, pathname, searchParams)
  );
  const activeDescendant = childActive && !expanded;

  return (
    <TreeRow
      item={item}
      active={active}
      depth={depth}
      hasChildren
      expanded={expanded}
      onToggle={() => setExpanded(!expanded)}
      activeDescendant={activeDescendant}
      onNavigate={onNavigate}
    >
      {item.children!.map((child) => (
        <SidebarLink
          key={child.href}
          item={child}
          active={routeIsActive(child.href!, pathname, searchParams)}
          onNavigate={onNavigate}
        />
      ))}
    </TreeRow>
  );
}

'''
s = s.replace("function RenderNavItems({", comp + "function RenderNavItems({")
open(p,'w').write(s)
print('done')
