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

#include <QObject>
#include <QJsonObject>

class QProcess;

/**
 * Small Qt wrapper around the Python bridge process.
 *
 * Uses blocking request/response calls for one-shot commands and a dedicated
 * long-running process for export progress events.
 */
class BridgeClient : public QObject {
  Q_OBJECT

public:
  /**
   * Construct a bridge client instance.
   *
   * @param parent Optional Qt parent object.
   */
  explicit BridgeClient(QObject *parent = nullptr);

  /**
   * Execute a one-shot bridge command and return its JSON object payload.
   *
   * @param command Bridge subcommand name.
   * @param payload JSON request object written to stdin.
   * @param error Optional output string for user-displayable errors.
   * @return Parsed JSON object payload on success, or an empty object on error.
   */
  QJsonObject call(const QString &command, const QJsonObject &payload, QString *error = nullptr) const;

  /// Start a dedicated bridge process for a long-running export.
  void startExport(const QJsonObject &payload);
  /// Cancel the currently running export process.
  void cancelExport();
  /// Return whether an export bridge process is currently active.
  bool isExportRunning() const;

signals:
  /// Emitted when the bridge reports export progress.
  void exportProgress(int current, int total, int percent);
  /// Emitted when the bridge reports export completion.
  void exportCompleted();
  /// Emitted when the bridge reports an export error.
  void exportError(const QString &message);

private slots:
  /// Consume buffered NDJSON export output from the bridge process.
  void handleExportStdout();
  /// Finalize export state after the bridge process exits.
  void handleExportFinished(int exitCode);

private:
  /// Return the Python executable used to launch the bridge module.
  QString pythonExecutable() const;
  /// Build the argument vector for one bridge subcommand.
  QStringList bridgeArguments(const QString &command) const;
  /// Parse and dispatch a single NDJSON export event line.
  void processExportLine(const QByteArray &line);
  /// Dispose the finished export process and clear client-side state.
  void cleanupExportProcess();

  mutable QProcess *exportProcess_{nullptr};
  mutable QByteArray exportStdoutBuffer_;
  mutable bool exportSawTerminalEvent_{false};
  mutable bool cancelRequested_{false};
};
