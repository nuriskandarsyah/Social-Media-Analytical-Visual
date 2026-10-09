export default function Loading({
    text = "Memuat..."
}) {
    return (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-white/80 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-4">

                <div className="relative flex h-16 w-16 items-center justify-center">
                    <div className="absolute inset-0 animate-spin rounded-full border-4 border-gray-200 border-t-black" />

                    <span className="text-sm font-bold tracking-tight text-gray-900">
                        MAVis
                    </span>
                </div>

                <div className="text-sm font-medium text-gray-600">
                    {text}
                </div>

            </div>
        </div>
    );
}