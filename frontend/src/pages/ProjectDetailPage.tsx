import {
  useMemo,
  useState,
  type FormEvent,
} from "react";
import { Link, useParams } from "react-router-dom";

import { useCreateAgent } from "../features/agents/agent-mutations";
import { useAgents } from "../features/agents/agent-queries";
import { useProject } from "../features/projects/project-queries";
import { ApiError } from "../services/api-client";


function createSlug(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}


export function ProjectDetailPage() {
  const { projectId } = useParams();

  const {
    data: project,
    isLoading: isProjectLoading,
    isError: isProjectError,
  } = useProject(projectId ?? null);

  const {
    data: agents = [],
    isLoading: isAgentsLoading,
    isError: isAgentsError,
  } = useAgents(projectId ?? null);

  const createAgentMutation = useCreateAgent();

  const [isCreateFormOpen, setIsCreateFormOpen] =
    useState(false);

  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [isSlugEdited, setIsSlugEdited] = useState(false);
  const [formError, setFormError] =
    useState<string | null>(null);

  const normalizedSlug = useMemo(
    () => createSlug(slug),
    [slug],
  );

  function resetForm() {
    setName("");
    setSlug("");
    setDescription("");
    setIsSlugEdited(false);
    setFormError(null);
  }

  function handleNameChange(value: string) {
    setName(value);

    if (!isSlugEdited) {
      setSlug(createSlug(value));
    }
  }

  async function handleCreateAgent(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!projectId) {
      return;
    }

    const normalizedName = name.trim();

    if (!normalizedName) {
      setFormError("Agent name is required.");
      return;
    }

    if (!normalizedSlug) {
      setFormError("Agent slug is required.");
      return;
    }

    setFormError(null);

    try {
      await createAgentMutation.mutateAsync({
        projectId,
        agent: {
          name: normalizedName,
          slug: normalizedSlug,
          description: description.trim() || null,
        },
      });

      resetForm();
      setIsCreateFormOpen(false);
    } catch (error) {
      if (error instanceof ApiError) {
        setFormError(error.message);
      } else {
        setFormError(
          "Unable to register agent. Please try again.",
        );
      }
    }
  }

  if (isProjectLoading || isAgentsLoading) {
    return (
      <section className="page-section">
        <p>Loading project...</p>
      </section>
    );
  }

  if (isProjectError || !project) {
    return (
      <section className="page-section">
        <p>Unable to load project.</p>
      </section>
    );
  }

  return (
    <section className="page-section">
      <div className="project-detail-breadcrumb">
        <Link to="/app/projects">Projects</Link>
        <span>/</span>
        <span>{project.name}</span>
      </div>

      <div className="page-heading">
        <div>
          <p className="page-eyebrow">Project</p>

          <h1>{project.name}</h1>

          <p>
            Register and manage AI agents within this project.
          </p>
        </div>

        <button
          type="button"
          className="topbar-button"
          onClick={() => {
            setFormError(null);
            setIsCreateFormOpen((value) => !value);
          }}
        >
          {isCreateFormOpen
            ? "Cancel"
            : "Register Agent"}
        </button>
      </div>

      <div className="project-detail-summary">
        <div>
          <span>Project slug</span>
          <strong>{project.slug}</strong>
        </div>

        <div>
          <span>Status</span>
          <strong>
            {project.is_active ? "Active" : "Inactive"}
          </strong>
        </div>

        <div>
          <span>Agents</span>
          <strong>{agents.length}</strong>
        </div>
      </div>

      {isCreateFormOpen ? (
        <form
          className="project-create-form"
          onSubmit={handleCreateAgent}
        >
          <label>
            <span>Agent name</span>

            <input
              type="text"
              value={name}
              onChange={(event) =>
                handleNameChange(event.target.value)
              }
              maxLength={255}
              disabled={createAgentMutation.isPending}
              required
            />
          </label>

          <label>
            <span>Slug</span>

            <input
              type="text"
              value={slug}
              onChange={(event) => {
                setIsSlugEdited(true);
                setSlug(event.target.value);
              }}
              pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              maxLength={100}
              disabled={createAgentMutation.isPending}
              required
            />
          </label>

          <label>
            <span>Description</span>

            <textarea
              value={description}
              onChange={(event) =>
                setDescription(event.target.value)
              }
              maxLength={1000}
              disabled={createAgentMutation.isPending}
            />
          </label>

          {formError ? (
            <p role="alert">{formError}</p>
          ) : null}

          <button
            type="submit"
            className="topbar-button"
            disabled={createAgentMutation.isPending}
          >
            {createAgentMutation.isPending
              ? "Registering..."
              : "Register Agent"}
          </button>
        </form>
      ) : null}

      <div className="resource-section-heading">
        <div>
          <p className="page-eyebrow">Agents</p>
          <h2>Registered Agents</h2>
        </div>
      </div>

      {isAgentsError ? (
        <p>Unable to load agents.</p>
      ) : agents.length === 0 ? (
        <div className="empty-state">
          <h2>No agents yet</h2>
          <p>
            Register your first AI agent to begin creating
            versioned configurations and deployments.
          </p>
        </div>
      ) : (
        <div className="project-grid">
          {agents.map((agent) => (
            <Link
              key={agent.id}
              className="project-card project-card-link"
              to={`/app/agents/${agent.id}`}
            >
              <div className="project-card-header">
                <div>
                  <p className="project-slug">
                    {agent.slug}
                  </p>

                  <h2>{agent.name}</h2>
                </div>

                <span className="project-status">
                  {agent.status}
                </span>
              </div>

              <p className="project-description">
                {agent.description
                  ?? "No description provided."}
              </p>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
