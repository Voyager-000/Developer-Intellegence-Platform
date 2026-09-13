import { Button } from "@/components/ui/flow-hover-button";
import { Github } from "lucide-react";

export default function DemoOne() {
  return (
    <Button icon={<Github />}>
      Hover Over Me
    </Button>
  );
}
