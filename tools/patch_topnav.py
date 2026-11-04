p = 'frontend/src/components/admin/admin-top-nav.tsx'
s = open(p).read()
s = s.replace('import { useSearchParams } from "next/navigation";\n', '')
s = s.replace('  const searchParams = useSearchParams();\n', '')
open(p, 'w').write(s)
print('done')
