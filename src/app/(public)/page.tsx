import { DcHero } from "@/components/marketing/dc-hero";
import { DcCareerPaths } from "@/components/marketing/dc-career-paths";
import { DcFlexibility } from "@/components/marketing/dc-flexibility";
import { DcLearnByBuilding } from "@/components/marketing/dc-learn-by-building";
import { DcCredentials } from "@/components/marketing/dc-credentials";
import { DcStats } from "@/components/marketing/dc-stats";
import { DcTestimonials } from "@/components/marketing/dc-testimonials";
import { DcCatalog } from "@/components/marketing/dc-catalog";
import { DcCta } from "@/components/marketing/dc-cta";

export default function HomePage() {
  return (
    <>
      <DcHero />
      <DcCareerPaths />
      <DcFlexibility />
      <DcLearnByBuilding />
      <DcCredentials />
      <DcStats />
      <DcTestimonials />
      <DcCatalog />
      <DcCta />
    </>
  );
}
