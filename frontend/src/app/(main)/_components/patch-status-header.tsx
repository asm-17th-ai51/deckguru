import { getPatchInfo } from '@/api/get-patch-info/get';
import { Badge } from '@/components/ui/badge';
import type { PatchInfo } from '@/lib/schema';

const FALLBACK_PATCH_INFO: PatchInfo = {
  patch_version: 'unknown',
  last_updated: 'unknown',
  warnings: ['patch_info_unavailable'],
};

const formatLastUpdated = (value: string) => {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toISOString().slice(0, 10);
};

const resolvePatchInfo = async () => {
  try {
    return await getPatchInfo();
  } catch {
    return FALLBACK_PATCH_INFO;
  }
};

export async function PatchStatusHeader() {
  const patchInfo = await resolvePatchInfo();
  const hasWarnings = patchInfo.warnings.length > 0;

  return (
    <header className="absolute top-0 right-0 z-20 flex justify-end p-4 sm:p-6">
      <div className="flex flex-row flex-wrap justify-end gap-2">
        <Badge variant="outline" className="h-auto border-2 px-3 py-2">
          PATCH VERSION {patchInfo.patch_version}
        </Badge>
        <Badge variant="outline" className="h-auto border-2 px-3 py-2">
          LAST UPDATED {formatLastUpdated(patchInfo.last_updated)}
        </Badge>
        {hasWarnings ? (
          <Badge variant="destructive" className="h-auto border-2 px-3 py-2">
            DATA WARNING
          </Badge>
        ) : null}
      </div>
    </header>
  );
}
