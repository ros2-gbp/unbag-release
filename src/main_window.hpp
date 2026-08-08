// MIT License
//
// Copyright (c) 2026 Institute for Automotive Engineering (ika), RWTH Aachen University
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

#pragma once

#include <QJsonArray>
#include <QJsonObject>
#include <QMainWindow>

/**
 * Main GUI window for ros2_unbag.
 *
 * Hosts the three-column export workflow:
 * - left: bag loading, topic selection, config load/save
 * - middle: per-topic export settings
 * - right: global settings, summary, export/cancel controls
 */
class BridgeClient;
class ProcessorChainWidget;
class QEvent;
class QLabel;
class QLineEdit;
class QObject;
class QShowEvent;
class QTreeWidget;
class QTreeWidgetItem;
class QComboBox;
class QPushButton;
class QStackedWidget;
class QScrollArea;
class QMovie;
class QProgressBar;
class QSlider;
class QDoubleSpinBox;
class QStatusBar;
class QFrame;
class QToolButton;
class QWidget;
class QGroupBox;
class QTimer;
class QPixmap;

/**
 * Main application window coordinating bag inspection, config editing, and export.
 */
class MainWindow : public QMainWindow {
  Q_OBJECT

public:
  /**
   * Construct the main window and initialize the GUI.
   *
   * @param parent Optional Qt parent widget.
   */
  explicit MainWindow(QWidget *parent = nullptr);

private slots:
  /// Open a bag-selection dialog and inspect the selected bag through the bridge.
  void loadBag();
  /// Load the clicked topic into the middle-column editor.
  void handleTopicClicked(QTreeWidgetItem *item, int column);
  /// Keep selection state, summary, and per-topic config in sync with tree changes.
  void handleTopicChanged(QTreeWidgetItem *item, int column);
  /// Refresh mode controls and defaults after a format change.
  void handleFormatChanged();
  /// Adjust naming defaults after a mode change.
  void handleModeChanged();
  /// Change the shared base output directory for all topic configs.
  void handleBaseDirectoryChange();
  /// Save the current GUI configuration as JSON.
  void saveConfigFile();
  /// Load a JSON config file into the current bag context.
  void loadConfigFile();
  /// Validate the current selection and start the export worker process.
  void startExport();
  /// Cancel the currently running export.
  void cancelExport();

  /// Update progress visuals from a bridge progress event.
  void handleExportProgress(int current, int total, int percent);
  /// Finalize UI state after a successful export.
  void handleExportCompleted();
  /// Finalize UI state after an export error or cancellation.
  void handleExportError(const QString &message);

private:
  /// Build the complete widget tree and wire signal/slot connections.
  void buildUi();
  /// Apply the packaged Qt stylesheet.
  void applyStyleSheet();
  /// Track scroll viewport resizes used for placeholder image scaling.
  bool eventFilter(QObject *watched, QEvent *event) override;
  /// Trigger post-show layout-dependent UI adjustments.
  void showEvent(QShowEvent *event) override;
  /// Keep responsive UI details sized correctly during window resize.
  void resizeEvent(QResizeEvent *event) override;
  /// Replace the current bag metadata and rebuild topic UI state.
  void setBagData(const QJsonObject &bagData);
  /// Toggle export-running UI state.
  void setExportRunning(bool running);
  /// Enable or disable controls based on bag/loading/export state.
  void updateUiAvailability();
  /// Show the empty topic-settings placeholder view.
  void showTopicPlaceholder();
  /// Show the per-topic settings editor view.
  void showTopicEditor();
  /// Recompute selected-topic summary and master-topic choices.
  void updateSummary();
  /// Rebuild the resampling master-topic combo from selected topics.
  void updateMasterTopics();
  /// Show a transient feedback banner.
  void setFeedback(const QString &message, const QString &type);
  /// Hide the feedback banner.
  void clearFeedback();
  /// Refresh the elided base-directory label text.
  void updateBaseDirLabel();
  /// Scale the title placeholder image to the available middle-column width.
  void updatePlaceholderPixmap();
  /// Keep the status-bar progress widget sized relative to window width.
  void updateStatusProgressWidth();
  /// Switch the UI into a loading/progress state.
  void showStatusProgress(const QString &message, bool indeterminate);
  /// Leave the loading/progress state and restore the settings page.
  void hideStatusProgress(const QString &message = QString());
  /// Persist the editor contents into the current topic config map.
  void saveCurrentTopicConfig();
  /// Load a topic config into the editor widgets.
  void loadTopicIntoEditor(const QString &topicName);
  /// Return the effective config for a topic, including defaults.
  QJsonObject effectiveTopicConfig(const QString &topicName) const;
  /// Read the current editor widgets into a topic config object.
  QJsonObject currentEditorConfig() const;
  /// Apply a topic config object to the editor widgets.
  void applyEditorConfig(const QString &topicName, const QJsonObject &config);
  /// Refresh mode choices for a given topic format.
  void refreshModeControls(const QString &topicName, const QString &formatName, const QString &selectedMode);
  /// Return the default mode name for a topic format.
  QString defaultModeForFormat(const QJsonObject &topicMeta, const QString &formatName) const;
  /// Look up bag metadata for one topic.
  QJsonObject topicMeta(const QString &topicName) const;
  /// Build the normalized bridge payload from current UI state.
  QJsonObject selectedPayload() const;
  /// Select the topic item matching the given topic name.
  void selectTopicItem(const QString &topicName);
  /// Return whether a topic is currently marked for export.
  bool isTopicChecked(const QString &topicName) const;
  /// Set a topic export checkbox while optionally suppressing signal reactions.
  void setTopicChecked(const QString &topicName, bool checked, bool blockSignals = false);
  /// Update the export badge styling for the current topic.
  void updateBadgeState(bool checked);
  /// Mark invalid editor fields using widget properties/styles.
  void updateValidationStyles();
  /// Filter the topic tree by the given text.
  void applyProxyFilter(const QString &text);

  BridgeClient *bridge_;
  QJsonObject bagData_;
  QJsonObject topicConfigs_;
  QString currentTopic_;
  QString bagPath_;
  QString baseDirectory_;
  bool updatingTree_{false};
  bool bagLoading_{false};
  bool exportRunning_{false};

  QTreeWidget *topicTree_;
  QLineEdit *topicFilterEdit_;
  QPushButton *selectAllButton_;
  QPushButton *selectNoneButton_;
  QPushButton *loadBagButton_;
  QPushButton *loadBagSecondaryButton_;
  QLabel *bagNameLabel_;
  QPushButton *loadConfigButton_;
  QPushButton *saveConfigButton_;

  QScrollArea *middleScrollArea_;
  QStackedWidget *middleStack_;
  QLabel *loadingLabel_;
  QLabel *loadingPercentLabel_;
  QMovie *loadingMovie_;
  QWidget *settingsPage_;
  QLabel *topicLabel_;
  QPushButton *exportBadgeButton_;
  QWidget *topicFormWidget_;
  QComboBox *formatCombo_;
  QComboBox *modeCombo_;
  QLabel *modeLabel_;
  QLineEdit *pathEdit_;
  QLineEdit *subdirEdit_;
  QLineEdit *namingEdit_;
  ProcessorChainWidget *processorChainWidget_;
  QLabel *placeholderLabel_;
  QLabel *placeholderHintLabel_;
  QLabel *helpTextLabel_;
  QPixmap *placeholderPixmap_;

  QGroupBox *settingsGroup_;
  QGroupBox *baseGroup_;
  QGroupBox *summaryGroup_;
  QSlider *cpuSlider_;
  QDoubleSpinBox *cpuSpin_;
  QComboBox *assocCombo_;
  QLineEdit *epsEdit_;
  QComboBox *masterCombo_;
  QLabel *baseDirLabel_;
  QPushButton *baseDirButton_;
  QLabel *summaryLabel_;
  QFrame *feedbackBanner_;
  QLabel *feedbackLabel_;
  QToolButton *feedbackCloseButton_;
  QTimer *feedbackTimer_;
  QPushButton *exportButton_;
  QPushButton *cancelButton_;

  QStatusBar *statusBar_;
  QProgressBar *statusProgress_;
};
