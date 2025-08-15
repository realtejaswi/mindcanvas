import React, { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

const Dashboard = () => {
  const [searches, setSearches] = useState([]);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('searches');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [searchData, imageData] = await Promise.all([
        dashboardAPI.getSearches(0, 20),
        dashboardAPI.getImages(0, 20)
      ]);
      setSearches(searchData);
      setImages(imageData);
    } catch (error) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (type, id) => {
    try {
      if (type === 'search') {
        await dashboardAPI.deleteSearch(id);
        setSearches(searches.filter(s => s.id !== id));
      } else {
        await dashboardAPI.deleteImage(id);
        setImages(images.filter(i => i.id !== id));
      }
    } catch (error) {
      setError(`Failed to delete ${type}`);
    }
  };

  const handleExport = async (format, dataType = 'all') => {
    try {
      let blob;
      let filename;

      if (format === 'csv') {
        blob = await dashboardAPI.exportCSV(dataType);
        filename = 'mindcanvas_data.csv';
      } else {
        blob = await dashboardAPI.exportPDF(dataType);
        filename = 'mindcanvas_data.pdf';
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      setError(`Failed to export ${format.toUpperCase()}`);
    }
  };

  const filteredSearches = searches.filter(search =>
    search.query.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredImages = images.filter(image =>
    image.prompt.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <LoadingSpinner text="Loading dashboard..." />;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Dashboard</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Manage your search and image generation history
        </p>
      </div>

      <ErrorMessage message={error} onDismiss={() => setError('')} />

      {/* Export Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Export Data
        </h2>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => handleExport('csv')}
            className="btn-primary"
          >
            Export CSV
          </button>
          <button
            onClick={() => handleExport('pdf')}
            className="btn-primary"
          >
            Export PDF
          </button>
          <button
            onClick={() => handleExport('csv', 'searches')}
            className="btn-secondary"
          >
            Export Searches Only
          </button>
          <button
            onClick={() => handleExport('csv', 'images')}
            className="btn-secondary"
          >
            Export Images Only
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search your history..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        />
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200 dark:border-gray-600">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('searches')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'searches'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              Searches ({filteredSearches.length})
            </button>
            <button
              onClick={() => setActiveTab('images')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'images'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              Images ({filteredImages.length})
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      {activeTab === 'searches' ? (
        <div className="space-y-4">
          {filteredSearches.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              No searches found
            </div>
          ) : (
            filteredSearches.map((search) => (
              <div
                key={search.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                      {search.query}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      {new Date(search.created_at).toLocaleDateString()} at{' '}
                      {new Date(search.created_at).toLocaleTimeString()}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">
                      {search.results?.results?.length || 0} results found
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete('search', search.id)}
                    className="btn-danger"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredImages.length === 0 ? (
            <div className="col-span-full text-center py-8 text-gray-500 dark:text-gray-400">
              No images found
            </div>
          ) : (
            filteredImages.map((image) => (
              <div
                key={image.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden"
              >
                {image.image_data && (
                  <img
                    src={`data:image/png;base64,${image.image_data}`}
                    alt={image.prompt}
                    className="w-full h-48 object-cover"
                  />
                )}
                <div className="p-4">
                  <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2">
                    {image.prompt}
                  </h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    {new Date(image.created_at).toLocaleDateString()}
                  </p>
                  <button
                    onClick={() => handleDelete('image', image.id)}
                    className="btn-danger mt-3 w-full text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;