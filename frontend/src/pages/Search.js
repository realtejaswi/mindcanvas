import React, { useState } from 'react';
import { searchAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

const Search = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');

    try {
      const searchResults = await searchAPI.search(query, 10);
      setResults(searchResults);
    } catch (error) {
      setError('Failed to perform search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Web Search</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Search the web for information on any topic
        </p>
      </div>

      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What would you like to search for?"
            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="btn-primary px-8"
          >
            {loading ? <LoadingSpinner size="small" text="" /> : 'Search'}
          </button>
        </div>
      </form>

      <ErrorMessage message={error} onDismiss={() => setError('')} />

      {results && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Search Results
            </h2>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {results.total_results} results found
            </span>
          </div>

          <div className="space-y-4">
            {results.results.map((result, index) => (
              <div
                key={index}
                className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 hover:shadow-md transition-shadow"
              >
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-primary-600 dark:hover:text-primary-400"
                  >
                    {result.title}
                  </a>
                </h3>
                <p className="text-sm text-primary-600 dark:text-primary-400 mb-3">
                  {result.url}
                </p>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                  {result.content}
                </p>
                {result.score && (
                  <div className="mt-3 flex items-center">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      Relevance: {Math.round(result.score * 100)}%
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;