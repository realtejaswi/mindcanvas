import React, { useState } from 'react';
import { imageAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

const ImageGeneration = () => {
  const [prompt, setPrompt] = useState('');
  const [settings, setSettings] = useState({
    width: 512,
    height: 512,
    steps: 20
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError('');

    try {
      const imageResult = await imageAPI.generate(
        prompt,
        settings.width,
        settings.height,
        settings.steps
      );
      setResult(imageResult);
    } catch (error) {
      setError('Failed to generate image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSettingChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: parseInt(value) || 0
    }));
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Image Generation</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Generate AI images from text descriptions
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="space-y-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Image Description
              </label>
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the image you want to generate..."
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                disabled={loading}
              />
            </div>

            {/* Settings */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="width" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Width
                </label>
                <select
                  id="width"
                  value={settings.width}
                  onChange={(e) => handleSettingChange('width', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  disabled={loading}
                >
                  <option value={256}>256px</option>
                  <option value={512}>512px</option>
                  <option value={768}>768px</option>
                  <option value={1024}>1024px</option>
                </select>
              </div>

              <div>
                <label htmlFor="height" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Height
                </label>
                <select
                  id="height"
                  value={settings.height}
                  onChange={(e) => handleSettingChange('height', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                  disabled={loading}
                >
                  <option value={256}>256px</option>
                  <option value={512}>512px</option>
                  <option value={768}>768px</option>
                  <option value={1024}>1024px</option>
                </select>
              </div>
            </div>

            <div>
              <label htmlFor="steps" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Steps: {settings.steps}
              </label>
              <input
                type="range"
                id="steps"
                min="10"
                max="50"
                value={settings.steps}
                onChange={(e) => handleSettingChange('steps', e.target.value)}
                className="w-full"
                disabled={loading}
              />
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>Faster</span>
                <span>Higher Quality</span>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !prompt.trim()}
              className="w-full btn-primary py-3"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <LoadingSpinner size="small" text="" />
                  <span className="ml-2">Generating Image...</span>
                </div>
              ) : (
                'Generate Image'
              )}
            </button>
          </form>

          <ErrorMessage message={error} onDismiss={() => setError('')} />
        </div>

        {/* Result Display */}
        <div className="space-y-6">
          {result && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                Generated Image
              </h3>

              {result.image_data ? (
                <div className="space-y-4">
                  <img
                    src={`data:image/png;base64,${result.image_data}`}
                    alt={result.prompt}
                    className="w-full rounded-lg shadow-md"
                  />
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <p><strong>Prompt:</strong> {result.prompt}</p>
                    <p><strong>Dimensions:</strong> {settings.width} × {settings.height}</p>
                    <p><strong>Steps:</strong> {settings.steps}</p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No image data received
                </div>
              )}
            </div>
          )}

          {loading && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="text-center py-8">
                <LoadingSpinner size="large" text="Generating your image..." />
                <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                  This may take a few moments depending on the complexity of your prompt.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageGeneration;