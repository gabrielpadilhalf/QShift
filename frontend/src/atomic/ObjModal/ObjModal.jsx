import { Button } from "../AtmButton/index.js";
import { X } from "lucide-react";
import { AtmDivider } from "../AtmDivider/Divider.jsx";
import { AtmText } from "../AtmText/Text.jsx";

export function ObjModal({ title, children, onClose }) {
    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-slate-800 rounded-lg border border-slate-700 max-w-md w-full shadow-xl">
                <div className="flex items-center justify-between p-6">
                    <div className="flex items-center gap-3">
                        <AtmText as="h3" size="lg" weight="semibold" color="white">
                            {title}
                        </AtmText>
                    </div>
                    <Button onClick={onClose} variant='ghost'>
                        <X size={24} />
                    </Button>
                </div>
                <AtmDivider />
                {children}
            </div>
        </div>
    );
}