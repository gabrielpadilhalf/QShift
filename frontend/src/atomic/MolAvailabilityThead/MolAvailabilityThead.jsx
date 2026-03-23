import { AtmText } from '../AtmText/index.js';

/**
 * MolAvailabilityThead – availability legend: "Select Availability" + color legend
 */
export function MolAvailabilityThead() {
    return (
        <div className="mb-6 flex items-center justify-between">
            <div>
                <AtmText as="h3" size="lg" weight="semibold" className="mb-1">Select Availability</AtmText>
                <AtmText as="p" size="sm" color="muted">Click and drag to mark available times.</AtmText>
            </div>
            <div className="flex gap-4 text-sm">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-green-500 rounded" />
                    <AtmText color="dimmer">Available</AtmText>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-slate-900/40 border border-slate-600 rounded" />
                    <AtmText color="dimmer">Unavailable</AtmText>
                </div>
            </div>
        </div>
    );
}