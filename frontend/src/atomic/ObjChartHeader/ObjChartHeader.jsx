import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '../AtmButton/index.js';
import { METRIC_COLORS, STATS_CONFIG } from '../../constants/employeeStatsConfig.js';
import { months } from '../../constants/constantsOfTable.js';
import { AtmText } from '../AtmText/Text.jsx';
import { MolMetricSelector } from '../MolMetricSelector';

export function ObjChartHeader({
    selectedMetric,
    setSelectedMetric,
    currentMonth,
    currentYear,
    onPrevMonth,
    onNextMonth,
    onPrevYear,
    onNextYear,
}) {
    return (
        <div className="bg-slate-800 rounded-lg px-4 py-3 border border-slate-700">
            <div className="flex flex-col lg:flex-row items-center mb-4 gap-4">
                <AtmText as="h3" size="lg" weight="semibold" color="white">
                    Select Metric to Display
                </AtmText>
                <div className="flex flex-col sm:flex-row items-center gap-4 w-full lg:w-auto lg:ml-auto">
                    <div className="flex items-center justify-center gap-2 w-full sm:w-auto">
                        <Button onClick={onPrevMonth} variant="periodNav" title="Previous month">
                            <ChevronLeft size={24} className="text-white" />
                        </Button>
                        <AtmText as="span" size="xl" weight="medium" color="white" className="min-w-[120px] text-center">
                            {months[currentMonth - 1]}
                        </AtmText>
                        <Button onClick={onNextMonth} variant="periodNav" title="Next month">
                            <ChevronRight size={24} className="text-white" />
                        </Button>
                    </div>
                    <div className="flex items-center justify-center gap-2 w-full sm:w-auto">
                        <Button onClick={onPrevYear} variant="periodNav" title="Previous Year">
                            <ChevronLeft size={24} className="text-white" />
                        </Button>
                        <AtmText as="span" size="xl" weight="medium" color="white" className="min-w-[80px] text-center">
                            {currentYear}
                        </AtmText>
                        <Button onClick={onNextYear} variant="periodNav" title="Next Year">
                            <ChevronRight size={24} className="text-white" />
                        </Button>
                    </div>
                </div>
            </div>

            <MolMetricSelector
                metrics={STATS_CONFIG}
                selectedMetric={selectedMetric}
                onSelect={setSelectedMetric}
                colors={METRIC_COLORS}
            />
        </div>
    );
}

