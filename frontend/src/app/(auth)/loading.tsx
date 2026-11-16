import { CometSpinner } from "@/components/ui/comet-spinner";

export default function AuthLoading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <CometSpinner className="h-10 w-10" />
    </div>
  );
}
