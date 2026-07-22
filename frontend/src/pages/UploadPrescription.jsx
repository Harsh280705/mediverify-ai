import { useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import PageShell from '../components/PageShell';
import PrimaryButton from '../components/PrimaryButton';
import SectionCard from '../components/SectionCard';
import { apiClient } from '../services/api';
import { ROUTE_PATHS } from '../utils/constants';

export default function UploadPrescription() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [step, setStep] = useState(0); // 0: Idle, 1: OCR Processing, 2: AI Structure Extraction, 3: Success
  const [error, setError] = useState('');

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    setError('');
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    const extension = selectedFile.name.split('.').pop().toLowerCase();
    
    if (validTypes.includes(selectedFile.type) || ['jpg', 'jpeg', 'png', 'pdf'].includes(extension)) {
      setFile(selectedFile);
    } else {
      setError('Invalid file type. Only JPG, JPEG, PNG, and PDF files are allowed.');
      setFile(null);
    }
  };

  const handleSelectClick = () => {
    fileInputRef.current.click();
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setStep(1); // Starting OCR
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Step 1: Upload and extract text via PaddleOCR
      const uploadRes = await apiClient.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const rawText = uploadRes.data.text;
      if (!rawText) {
        throw new Error('No text could be extracted from the document. Please try a different scan.');
      }

      // Step 2: Send raw text to LLM (Ollama)
      setStep(2);
      const extractRes = await apiClient.post('/api/documents/extract', {
        text: rawText,
      });

      setStep(3); // Success
      
      // Navigate to Review page with the structured extraction data
      navigate(ROUTE_PATHS.REVIEW_PRESCRIPTION, {
        state: {
          extractedData: extractRes.data,
          fileName: file.name,
        },
      });
    } catch (err) {
      setStep(0);
      const msg = err.response?.data?.detail || err.message || 'An error occurred during prescription processing.';
      setError(msg);
    }
  };

  return (
    <PageShell
      eyebrow="Prescription Pipeline"
      title="Upload Prescription"
      description="Upload a photo or scanned PDF of your prescription. Our local OCR engine and AI model will parse and extract your medications automatically."
    >
      <div className="mx-auto max-w-2xl space-y-6">
        <SectionCard
          title="Prescription Document"
          footer={
            <div className="flex items-center justify-between">
              <Link
                to={ROUTE_PATHS.PATIENT_DASHBOARD}
                className="text-sm text-slate-400 hover:text-white"
              >
                Back to Dashboard
              </Link>
              {file && step === 0 && (
                <PrimaryButton onClick={handleUpload}>
                  Upload & Process
                </PrimaryButton>
              )}
            </div>
          }
        >
          <div className="space-y-4">
            {step === 0 ? (
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={handleSelectClick}
                className={`relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition cursor-pointer ${
                  dragActive
                    ? 'border-cyan-400 bg-cyan-950/20'
                    : 'border-white/10 bg-white/5 hover:border-white/20'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".jpg,.jpeg,.png,.pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />

                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-300">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="h-6 w-6"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z"
                    />
                  </svg>
                </div>

                <div className="mt-4">
                  <p className="text-sm font-medium text-slate-200">
                    <span className="text-cyan-400">Click to upload</span> or drag and drop
                  </p>
                  <p className="mt-1 text-xs text-slate-400">
                    Supports JPG, JPEG, PNG, or PDF files
                  </p>
                </div>
              </div>
            ) : (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center space-y-6">
                <div className="relative mx-auto flex h-16 w-16 items-center justify-center">
                  <div className="absolute h-full w-full animate-spin rounded-full border-4 border-cyan-400/20 border-t-cyan-400"></div>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="h-6 w-6 text-cyan-300"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                    />
                  </svg>
                </div>

                <div className="space-y-2">
                  <h3 className="text-base font-semibold text-white">
                    Processing Prescription
                  </h3>
                  <div className="flex flex-col items-center gap-1.5 text-sm text-slate-300">
                    <div className="flex items-center gap-2">
                      <span className={`h-2.5 w-2.5 rounded-full ${step >= 1 ? 'bg-cyan-400 animate-pulse' : 'bg-slate-600'}`} />
                      <span className={step === 1 ? 'text-white font-medium' : 'text-slate-400'}>
                        Step 1: Reading document using OCR
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`h-2.5 w-2.5 rounded-full ${step >= 2 ? 'bg-cyan-400 animate-pulse' : 'bg-slate-600'}`} />
                      <span className={step === 2 ? 'text-white font-medium' : 'text-slate-400'}>
                        Step 2: Structuring data using Ollama LLM
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {file && step === 0 && (
              <div className="flex items-center justify-between rounded-xl bg-white/5 p-4 border border-white/5">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-cyan-950/40 p-2 text-cyan-300">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="h-5 w-5"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{file.name}</p>
                    <p className="text-xs text-slate-400">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-white/10 hover:text-white"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="h-5 w-5"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            )}

            {error && (
              <div className="rounded-xl border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-300">
                {error}
              </div>
            )}
          </div>
        </SectionCard>
      </div>
    </PageShell>
  );
}
