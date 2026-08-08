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

#include <QFrame>
#include <QJsonArray>
#include <QJsonObject>
#include <QWidget>

class QComboBox;
class QFormLayout;
class QLabel;
class QPushButton;
class QToolButton;
class QVBoxLayout;

class ProcessorChainWidget;

/**
 * One editable processor entry inside a processor chain.
 *
 * Stores the selected processor plus any argument inputs for that processor.
 */
class ProcessorEntryWidget : public QFrame {
  Q_OBJECT

public:
  /**
   * Construct one processor entry widget.
   *
   * @param chainWidget Owning processor chain widget.
   */
  explicit ProcessorEntryWidget(ProcessorChainWidget *chainWidget);

  /// Update the displayed 1-based index and move-button state.
  void setIndex(int index, int total);
  /// Apply a saved processor config to the entry UI.
  void applyConfig(const QJsonObject &config);
  /// Select the first available processor definition.
  void selectDefault();
  /// Serialize the current entry UI state into a config object.
  QJsonObject config() const;

private slots:
  /// Rebuild argument inputs after the selected processor changes.
  void onProcessorChanged(const QString &processorName);

private:
  /// Remove all dynamic argument input rows.
  void clearArgs();
  /// Look up the processor definition for one processor name.
  QJsonObject processorDefinition(const QString &name) const;

  ProcessorChainWidget *chainWidget_;
  QLabel *indexLabel_;
  QComboBox *combo_;
  QToolButton *upButton_;
  QToolButton *downButton_;
  QToolButton *removeButton_;
  QFormLayout *argsLayout_;
  QList<QPair<QString, class QLineEdit *>> argInputs_;
};

/**
 * Editor widget for ordered per-topic processor chains.
 */
class ProcessorChainWidget : public QWidget {
  Q_OBJECT

public:
  /**
   * Construct the processor chain editor widget.
   *
   * @param parent Optional Qt parent widget.
   */
  explicit ProcessorChainWidget(QWidget *parent = nullptr);

  /// Replace the available processor definitions for the current topic type.
  void setProcessorDefinitions(const QJsonArray &definitions);
  /// Replace the current chain entries from saved config.
  void setChain(const QJsonArray &configs);
  /// Serialize the current chain to JSON config.
  QJsonArray chain() const;
  /// Return available processor names for the current topic type.
  QStringList availableProcessorNames() const;
  /// Look up one processor definition by name.
  QJsonObject processorDefinition(const QString &name) const;

signals:
  /// Emitted whenever the chain contents or order changes.
  void changed();

private slots:
  /// Append a new empty processor entry.
  void addEntry();

private:
  /// Append a new processor entry using an optional preset config.
  void addEntry(const QJsonObject &preset);
  /// Remove one processor entry from the chain.
  void removeEntry(ProcessorEntryWidget *entry);
  /// Move one processor entry up or down by one position.
  void moveEntry(ProcessorEntryWidget *entry, int delta);
  /// Refresh entry indices and move-button states.
  void reindexEntries();
  /// Show or hide the empty-state hint.
  void updateEmptyHint();

  friend class ProcessorEntryWidget;

  QJsonArray processorDefinitions_;
  QList<ProcessorEntryWidget *> entries_;
  QVBoxLayout *chainLayout_;
  QLabel *emptyHint_;
  QPushButton *addButton_;
};
