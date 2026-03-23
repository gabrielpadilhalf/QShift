import { SelectableButton } from '../AtmButton/index.js';

export function MolMetricSelector({ metrics, selectedMetric, onSelect, colors }) {
    return (
        <div className="flex gap-1.5 flex-wrap">
            {metrics.map((metric) => (
                <SelectableButton
                    key={metric.key}
                    size="md"
                    selected={selectedMetric === metric.key}
                    className={selectedMetric === metric.key ? colors[metric.key].bgButton + '' : ''}
                    onClick={() => onSelect(metric.key)}
                >
                    {metric.label}
                </SelectableButton>
            ))}
        </div>
    );
}