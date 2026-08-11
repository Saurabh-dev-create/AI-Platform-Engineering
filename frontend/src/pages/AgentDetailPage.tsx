import {
  useState,
  type FormEvent,
} from "react";
import { Link, useParams } from "react-router-dom";

import {
  useCreateAgentVersion,
  useDeprecateAgentVersion,
  usePublishAgentVersion,
} from "../features/agent-versions/agent-version-mutations";
import { useCreateDeployment } from "../features/deployments/deployment-mutations";
import { useDeploymentsForVersion } from "../features/deployments/deployment-queries";
import {
  type DeploymentEnvironment,
  type DeploymentStrategy,
} from "../features/deployments/deployment-service";
import { useAgentVersions } from "../features/agent-versions/agent-version-queries";
import { useAgent } from "../features/agents/agent-queries";
import { ApiError } from "../services/api-client";


function parseJsonObject(
  value: string,
  fieldName: string,
): Record<string, unknown> {
  const parsed = JSON.parse(value);

  if (
    typeof parsed !== "object"
    || parsed === null
    || Array.isArray(parsed)
  ) {
    throw new Error(
      `${fieldName} must be a JSON object.`,
    );
  }

  return parsed as Record<string, unknown>;
}


export function AgentDetailPage() {
  const { agentId } = useParams();

  const {
    data: agent,
    isLoading,
    isError,
  } = useAgent(agentId ?? null);

  const {
    data: versions = [],
    isLoading: isVersionsLoading,
    isError: isVersionsError,
  } = useAgentVersions(agentId ?? null);

  const createVersionMutation = useCreateAgentVersion();

  const publishVersionMutation =
    usePublishAgentVersion(agentId ?? "");

  const deprecateVersionMutation =
    useDeprecateAgentVersion(agentId ?? "");

  const [versionActionError, setVersionActionError] =
    useState<string | null>(null);

  const createDeploymentMutation =
    useCreateDeployment();

  const [deploymentVersionId, setDeploymentVersionId] =
    useState<string | null>(null);

  const [deploymentEnvironment, setDeploymentEnvironment] =
    useState<DeploymentEnvironment>("development");

  const [deploymentStrategy, setDeploymentStrategy] =
    useState<DeploymentStrategy>("rolling");

  const [deploymentError, setDeploymentError] =
    useState<string | null>(null);

  const {
    data: selectedVersionDeployments = [],
  } = useDeploymentsForVersion(deploymentVersionId);

  const [isCreateVersionOpen, setIsCreateVersionOpen] =
    useState(false);

  const [modelConfig, setModelConfig] =
    useState(`{
  "provider": "openai",
  "model": "gpt-4o-mini"
}`);

  const [promptTemplate, setPromptTemplate] =
    useState("");

  const [runtimeConfig, setRuntimeConfig] =
    useState(`{
  "timeout_seconds": 30
}`);

  const [toolConfig, setToolConfig] =
    useState("{}");

  const [changeSummary, setChangeSummary] =
    useState("");

  const [versionFormError, setVersionFormError] =
    useState<string | null>(null);


  async function handleCreateVersion(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!agentId) {
      return;
    }

    setVersionFormError(null);

    try {
      const parsedModelConfig = parseJsonObject(
        modelConfig,
        "Model config",
      );

      const parsedRuntimeConfig = parseJsonObject(
        runtimeConfig,
        "Runtime config",
      );

      const parsedToolConfig = parseJsonObject(
        toolConfig,
        "Tool config",
      );

      await createVersionMutation.mutateAsync({
        agentId,
        version: {
          model_config: parsedModelConfig,
          prompt_template:
            promptTemplate.trim() || null,
          runtime_config: parsedRuntimeConfig,
          tool_config: parsedToolConfig,
          change_summary:
            changeSummary.trim() || null,
        },
      });

      setPromptTemplate("");
      setChangeSummary("");
      setVersionFormError(null);
      setIsCreateVersionOpen(false);
    } catch (error) {
      if (error instanceof ApiError) {
        setVersionFormError(error.message);
      } else if (error instanceof SyntaxError) {
        setVersionFormError(
          "One or more configuration fields contain invalid JSON.",
        );
      } else if (error instanceof Error) {
        setVersionFormError(error.message);
      } else {
        setVersionFormError(
          "Unable to create agent version.",
        );
      }
    }
  }


  async function handlePublishVersion(
    versionId: string,
  ) {
    setVersionActionError(null);

    try {
      await publishVersionMutation.mutateAsync(versionId);
    } catch (error) {
      if (error instanceof ApiError) {
        setVersionActionError(error.message);
      } else {
        setVersionActionError(
          "Unable to publish agent version.",
        );
      }
    }
  }


  async function handleCreateDeployment(
    versionId: string,
  ) {
    setDeploymentError(null);

    try {
      await createDeploymentMutation.mutateAsync({
        agent_version_id: versionId,
        environment: deploymentEnvironment,
        strategy: deploymentStrategy,
      });

      setDeploymentVersionId(versionId);
    } catch (error) {
      if (error instanceof ApiError) {
        setDeploymentError(error.message);
      } else {
        setDeploymentError(
          "Unable to create deployment.",
        );
      }
    }
  }


  async function handleDeprecateVersion(
    versionId: string,
  ) {
    setVersionActionError(null);

    try {
      await deprecateVersionMutation.mutateAsync(versionId);
    } catch (error) {
      if (error instanceof ApiError) {
        setVersionActionError(error.message);
      } else {
        setVersionActionError(
          "Unable to deprecate agent version.",
        );
      }
    }
  }


  if (isLoading || isVersionsLoading) {
    return (
      <section className="page-section">
        <p>Loading agent...</p>
      </section>
    );
  }


  if (isError || !agent) {
    return (
      <section className="page-section">
        <p>Unable to load agent.</p>
      </section>
    );
  }


  return (
    <section className="page-section">
      <div className="project-detail-breadcrumb">
        <Link to="/app/projects">Projects</Link>
        <span>/</span>

        <Link to={`/app/projects/${agent.project_id}`}>
          Project
        </Link>

        <span>/</span>
        <span>{agent.name}</span>
      </div>


      <div className="page-heading">
        <div>
          <p className="page-eyebrow">Agent</p>

          <h1>{agent.name}</h1>

          <p>
            {agent.description
              ?? "No description provided."}
          </p>
        </div>
      </div>


      <div className="project-detail-summary">
        <div>
          <span>Agent slug</span>
          <strong>{agent.slug}</strong>
        </div>

        <div>
          <span>Status</span>
          <strong>{agent.status}</strong>
        </div>

        <div>
          <span>Project</span>
          <strong>{agent.project_id}</strong>
        </div>
      </div>


      <div className="resource-section-heading">
        <div>
          <p className="page-eyebrow">Versions</p>
          <h2>Agent Versions</h2>
        </div>

        <button
          type="button"
          className="topbar-button"
          onClick={() => {
            setVersionFormError(null);
            setIsCreateVersionOpen((value) => !value);
          }}
        >
          {isCreateVersionOpen
            ? "Cancel"
            : "Create Version"}
        </button>
      </div>


      {isCreateVersionOpen ? (
        <form
          className="agent-version-form"
          onSubmit={handleCreateVersion}
        >
          <label>
            <span>Model config</span>

            <textarea
              value={modelConfig}
              onChange={(event) =>
                setModelConfig(event.target.value)
              }
              spellCheck={false}
              disabled={createVersionMutation.isPending}
              required
            />
          </label>

          <label className="agent-version-form-wide">
            <span>Prompt template</span>

            <textarea
              value={promptTemplate}
              onChange={(event) =>
                setPromptTemplate(event.target.value)
              }
              disabled={createVersionMutation.isPending}
              placeholder="You are a helpful AI assistant..."
            />
          </label>

          <label>
            <span>Runtime config</span>

            <textarea
              value={runtimeConfig}
              onChange={(event) =>
                setRuntimeConfig(event.target.value)
              }
              spellCheck={false}
              disabled={createVersionMutation.isPending}
              required
            />
          </label>

          <label>
            <span>Tool config</span>

            <textarea
              value={toolConfig}
              onChange={(event) =>
                setToolConfig(event.target.value)
              }
              spellCheck={false}
              disabled={createVersionMutation.isPending}
              required
            />
          </label>

          <label className="agent-version-form-wide">
            <span>Change summary</span>

            <textarea
              value={changeSummary}
              onChange={(event) =>
                setChangeSummary(event.target.value)
              }
              maxLength={1000}
              disabled={createVersionMutation.isPending}
              placeholder="Describe what changed in this version."
            />
          </label>

          {versionFormError ? (
            <p
              className="agent-version-form-error"
              role="alert"
            >
              {versionFormError}
            </p>
          ) : null}

          <button
            type="submit"
            className="topbar-button"
            disabled={createVersionMutation.isPending}
          >
            {createVersionMutation.isPending
              ? "Creating..."
              : "Create Version"}
          </button>
        </form>
      ) : null}


      {versionActionError ? (
        <p
          className="agent-version-form-error"
          role="alert"
        >
          {versionActionError}
        </p>
      ) : null}


      {isVersionsError ? (
        <p>Unable to load agent versions.</p>
      ) : versions.length === 0 ? (
        <div className="empty-state">
          <h2>No versions yet</h2>

          <p>
            Create the first version of this agent to define
            model, prompt, runtime, and tool configuration.
          </p>
        </div>
      ) : (
        <div className="project-grid">
          {versions.map((version) => (
            <article
              key={version.id}
              className="project-card"
            >
              <div className="project-card-header">
                <div>
                  <p className="project-slug">
                    Version {version.version_number}
                  </p>

                  <h2>
                    {version.change_summary
                      ?? `Agent version ${version.version_number}`}
                  </h2>
                </div>

                <span className="project-status">
                  {version.status}
                </span>
              </div>

              <p className="project-description">
                {version.prompt_template
                  ?? "No prompt template provided."}
              </p>

              <div className="agent-version-actions">
                {version.status === "draft" ? (
                  <button
                    type="button"
                    className="topbar-button"
                    disabled={
                      publishVersionMutation.isPending
                      || deprecateVersionMutation.isPending
                    }
                    onClick={() =>
                      void handlePublishVersion(version.id)
                    }
                  >
                    Publish
                  </button>
                ) : null}

                {version.status === "published" ? (
                  <>
                    <button
                      type="button"
                      className="topbar-button"
                      disabled={
                        publishVersionMutation.isPending
                        || deprecateVersionMutation.isPending
                        || createDeploymentMutation.isPending
                      }
                      onClick={() => {
                        setDeploymentError(null);

                        setDeploymentVersionId((current) =>
                          current === version.id
                            ? null
                            : version.id
                        );
                      }}
                    >
                      {deploymentVersionId === version.id
                        ? "Cancel Deploy"
                        : "Deploy"}
                    </button>

                    <button
                      type="button"
                      className="secondary-button"
                      disabled={
                        publishVersionMutation.isPending
                        || deprecateVersionMutation.isPending
                        || createDeploymentMutation.isPending
                      }
                      onClick={() =>
                        void handleDeprecateVersion(version.id)
                      }
                    >
                      Deprecate
                    </button>
                  </>
                ) : null}
              </div>

              {deploymentVersionId === version.id ? (
                <div className="deployment-create-panel">
                  <label>
                    <span>Environment</span>

                    <select
                      value={deploymentEnvironment}
                      onChange={(event) =>
                        setDeploymentEnvironment(
                          event.target.value as DeploymentEnvironment,
                        )
                      }
                      disabled={createDeploymentMutation.isPending}
                    >
                      <option value="development">
                        Development
                      </option>

                      <option value="staging">
                        Staging
                      </option>

                      <option value="production">
                        Production
                      </option>
                    </select>
                  </label>

                  <label>
                    <span>Strategy</span>

                    <select
                      value={deploymentStrategy}
                      onChange={(event) =>
                        setDeploymentStrategy(
                          event.target.value as DeploymentStrategy,
                        )
                      }
                      disabled={createDeploymentMutation.isPending}
                    >
                      <option value="rolling">
                        Rolling
                      </option>

                      <option value="blue_green">
                        Blue-green
                      </option>

                      <option value="canary">
                        Canary
                      </option>
                    </select>
                  </label>

                  {deploymentError ? (
                    <p
                      className="agent-version-form-error"
                      role="alert"
                    >
                      {deploymentError}
                    </p>
                  ) : null}

                  <button
                    type="button"
                    className="topbar-button"
                    disabled={createDeploymentMutation.isPending}
                    onClick={() =>
                      void handleCreateDeployment(version.id)
                    }
                  >
                    {createDeploymentMutation.isPending
                      ? "Creating..."
                      : "Create Deployment"}
                  </button>

                  {selectedVersionDeployments.length > 0 ? (
                    <div className="deployment-history">
                      <span>Deployments</span>

                      {selectedVersionDeployments.map(
                        (deployment) => (
                          <div
                            key={deployment.id}
                            className="deployment-history-item"
                          >
                            <strong>
                              {deployment.environment}
                            </strong>

                            <span>
                              {deployment.strategy}
                            </span>

                            <span>
                              {deployment.status}
                            </span>
                          </div>
                        ),
                      )}
                    </div>
                  ) : null}
                </div>
              ) : null}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
